
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Post, Category, Comment


class InkSpaceTestCase(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="varan",
            email="varan@example.com",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            username="another_user",
            email="other@example.com",
            password="TestPassword123!"
        )

        self.category = Category.objects.create(
            name="Technology",
            slug="technology"
        )

        self.post = Post.objects.create(
            title="Learning Django",
            content="This is a test article.",
            author=self.user,
            category=self.category,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now()
        )

    def test_homepage_loads(self):

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)

    def test_published_post_is_visible(self):

        response = self.client.get(
            reverse("post_detail", args=[self.post.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Learning Django")

    def test_dashboard_requires_login(self):

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_access_dashboard(self):

        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_user_can_create_post(self):

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("create_post"),
            {
                "title": "My New Article",
                "content": "This is my new article.",
                "category": self.category.id,
                "status": Post.Status.DRAFT,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Post.objects.filter(
                title="My New Article",
                author=self.user
            ).exists()
        )

    def test_user_cannot_edit_another_users_post(self):

        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("edit_post", args=[self.post.slug])
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_another_users_post(self):

        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("delete_post", args=[self.post.slug])
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Post.objects.filter(pk=self.post.pk).exists()
        )

    def test_comment_requires_approval(self):

        comment = Comment.objects.create(
            post=self.post,
            name="Test Reader",
            email="reader@example.com",
            body="Great article!"
        )

        self.assertFalse(comment.is_approved)

    def test_unpublished_post_is_not_public(self):

        draft = Post.objects.create(
            title="Private Draft",
            content="This is private.",
            author=self.user,
            status=Post.Status.DRAFT
        )

        response = self.client.get(
            reverse("post_detail", args=[draft.slug])
        )

        self.assertEqual(response.status_code, 404)
