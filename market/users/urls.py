from django.urls import path
from . import views
from .views import BrowsingHistory

app_name = "users"

urlpatterns = [
    path("register/", views.UserRegistrationView.as_view(), name="users_register"),
    path("login/", views.MyLoginView.as_view(), name="users_login"),
    path("logout/", views.UserLogoutView.as_view(), name="users_logout"),
    path("password/", views.RestorePasswordView.as_view(), name="users_restore_password"),
    path("account/", views.AccountView.as_view(), name="users_account"),
    path("profile/", views.MyProfileView.as_view(), name="users_profile"),
    # path('<id>/orders-history/'),
    # path('<id>/product-browsing-history/'),
    path("browsing-history/", BrowsingHistory.as_view(), name="browsing-history"),
]
