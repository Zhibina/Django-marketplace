from django.views import View

from users.services.users_service import MyProfileService as Service
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin

from users.forms import ChangePasswordForm, UserProfileForm
from users.models import CustomUser


class ProfileMixin(LoginRequiredMixin, FormMixin, View):
    form_class = ChangePasswordForm
    second_form_class = UserProfileForm
    template_name = "market/users/profile.jinja2"
    success_url = reverse_lazy("users:users_profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get(self, request):
        second_form = self.second_form_class(instance=request.user)
        user = CustomUser.objects.get(pk=request.user.pk)
        form = self.get_form()
        return render(request, self.template_name, {"form": form, "second_form": second_form, "user": user})

    def post(self, request):
        form = self.get_form()
        second_form = self.second_form_class(instance=request.user, data=request.POST, files=request.FILES)
        if Service.post_form_validation(form=form, second_form=second_form, request=self.request):
            return self.form_valid(form, second_form=second_form)
        return self.get(request)

    def form_valid(self, form, **kwargs):
        super().form_valid(form)
        return Service.form_validation(form=form, request=self.request, **kwargs)
