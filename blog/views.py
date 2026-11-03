
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .forms import RegisterForm, PostForm, CommentForm
from django.core.paginator import Paginator
from .models import Post, Category
from .forms import RegisterForm, PostForm


# 1. Homepage
def home(request):
    posts = Post.objects.filter(
        status=Post.Status.PUBLISHED,
        published_at__isnull=False
    ).select_related("author", "category")

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    categories = Category.objects.all()
    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    return render(request, "blog/home.html", {
        "posts": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "selected_category": category_slug,
    })


# 2. User registration
def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Your InkSpace account has been created successfully!"
            )

            return redirect("dashboard")

    else:
        form = RegisterForm()

    return render(request, "blog/register.html", {
        "form": form
    })


# 3. User dashboard
@login_required
def dashboard(request):

    posts = Post.objects.filter(
        author=request.user
    ).select_related("category")

    total_posts = posts.count()
    published_posts = posts.filter(
        status=Post.Status.PUBLISHED
    ).count()

    draft_posts = posts.filter(
        status=Post.Status.DRAFT
    ).count()

    return render(request, "blog/dashboard.html", {
        "posts": posts,
        "total_posts": total_posts,
        "published_posts": published_posts,
        "draft_posts": draft_posts,
    })


# 4. Create a blog post
@login_required
def create_post(request):

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)

            # Assign the logged-in user as author
            post.author = request.user

            # Manage publication timestamp
            if post.status == Post.Status.PUBLISHED:
                post.published_at = timezone.now()

            post.save()

            messages.success(
                request,
                "Your article has been created successfully!"
            )

            return redirect("dashboard")

    else:
        form = PostForm()

    return render(request, "blog/post_form.html", {
        "form": form,
        "page_title": "Create Article",
    })


# 5. Edit an existing post
@login_required
def edit_post(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug,
        author=request.user
    )

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():
            updated_post = form.save(commit=False)

            if updated_post.status == Post.Status.PUBLISHED:
                if not updated_post.published_at:
                    updated_post.published_at = timezone.now()
            else:
                updated_post.published_at = None

            updated_post.save()

            messages.success(
                request,
                "Your article has been updated successfully!"
            )

            return redirect("dashboard")

    else:
        form = PostForm(instance=post)

    return render(request, "blog/post_form.html", {
        "form": form,
        "page_title": "Edit Article",
    })


# 6. Delete a blog post
@login_required
def delete_post(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug,
        author=request.user
    )

    if request.method == "POST":
        post.delete()

        messages.success(
            request,
            "Your article has been deleted."
        )

        return redirect("dashboard")

    return render(request, "blog/post_confirm_delete.html", {
        "post": post
    })


# 7. View an individual published article

def post_detail(request, slug):

    post = get_object_or_404(
        Post.objects.select_related("author", "category"),
        slug=slug,
        status=Post.Status.PUBLISHED,
        published_at__isnull=False
    )

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            messages.success(
                request,
                "Your comment has been submitted for approval."
            )

            return redirect("post_detail", slug=post.slug)

    else:
        form = CommentForm()

    comments = post.comments.filter(
        is_approved=True
    )

    return render(request, "blog/post_detail.html", {
        "post": post,
        "comments": comments,
        "comment_form": form,
    })
