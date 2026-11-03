
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    # Public pages
    path("", views.home, name="home"),

    path(
        "blog/<slug:slug>/",
        views.post_detail,
        name="post_detail"
    ),

    # Authentication
    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="blog/login.html"
        ),
        name="login"
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),

    # Dashboard
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # Blog management
    path(
        "post/create/",
        views.create_post,
        name="create_post"
    ),

    path(
        "post/<slug:slug>/edit/",
        views.edit_post,
        name="edit_post"
    ),

    path(
        "post/<slug:slug>/delete/",
        views.delete_post,
        name="delete_post"
    ),
]
