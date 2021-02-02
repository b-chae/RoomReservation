import os
import requests
from django.conf import settings
from django.utils import translation
from django.http import HttpResponse
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, reverse, render
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(
                self.request, f"Welcome back {user.first_name}")
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    messages.info(request, f"See you later {request.user.first_name}")
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(
                self.request, f"Welcome back {user.first_name}")
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do : add success message
    except models.User.DoesNotExist:
        # to do : add error message
        pass

    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GH_ID")
    print(client_id)
    redirect_url = "http://airbnb-clone.eba-2kktntyc.ap-northeast-2.elasticbeanstalk.com/users/login/github/callback"
    return redirect(
        "https://github.com/login/oauth/authorize"
        + f"?client_id={client_id}"
        + f"&redirect_url={redirect_url}"
        + "&scope=read:user")


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code", None)
        if code is not None:
            result = requests.post(
                "https://github.com/login/oauth/access_token"
                + f"?client_id={client_id}"
                + f"&client_secret={client_secret}"
                + f"&code={code}",
                headers={"Accept": "application/json"},
            )
            result_json = result.json()
            error = result_json.get("error", None)
            if error is not None:
                raise GithubException("Can't get access token")
            else:
                access_token = result_json.get("access_token")
                api_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )

                profile_json = api_request.json()
                username = profile_json.get('login', None)
                if username is not None:
                    name = profile_json.get('name')
                    bio = profile_json.get('bio')
                    email = profile_json.get('email')
                    if bio is None:
                        bio = ""
                    if name is None:
                        name = "No Name"
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                f"You already have an account with {user.login_method}")
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(
                        request, f"Welcome back {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile")
        else:
            raise GithubException("Can't get authorization code")

    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("core:home"))


def kakao_login(request):
    client_id = os.environ.get("KAKAO_ID")
    redirect_uri = "http://airbnb-clone.eba-2kktntyc.ap-northeast-2.elasticbeanstalk.com/users/login/kakao/callback"
    return redirect(
        "https://kauth.kakao.com/oauth/authorize"
        + f"?client_id={client_id}"
        + f"&redirect_uri={redirect_uri}"
        + "&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://airbnb-clone.eba-2kktntyc.ap-northeast-2.elasticbeanstalk.com/users/login/kakao/callback"
        token_request = requests.get(
            "https://kauth.kakao.com/oauth/token?grant_type=authorization_code"
            + f"&client_id={client_id}"
            + f"&redirect_uri={redirect_uri}"
            + f"&code={code}"
        )

        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Can't get authorization code")
        access_token = token_json.get("access_token")

        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                'Authorization': f'Bearer {access_token}'
            },
        )
        profile_json = profile_request.json()

        try:
            email = profile_json.get("kakao_account").get("email", None)
            if email is None:
                raise KakaoException("Please also give me your email")
        except:
            raise KakaoException("Not allowed. Use email to login")

        nickname = profile_json.get("properties").get("nickname")
        profile_image = profile_json.get("properties").get("profile_image")

        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(
                    f"You already have an account with {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()

            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(f"{nickname}-avatar",
                                 ContentFile(photo_request.content))

        login(request, user)
        messages.success(
            request, f"Welcome back {user.first_name}")
        return redirect(reverse("core:home"))

    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UpdateProfile(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    template_name = "users/update-profile.html"
    fields = ("first_name", "last_name", "gender",
              "bio", "birthdate", "language", "currency")
    success_message = "Profile successfully updated!"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['first_name'].widget.attrs = {
            "placeholder": "First Name"
        }
        form.fields['last_name'].widget.attrs = {
            "placeholder": "Last Name"
        }
        form.fields['bio'].widget.attrs = {
            "placeholder": "Bio"
        }
        form.fields['birthdate'].widget.attrs = {
            "placeholder": "Birthdate(****-**-**)"
        }
        return form


class UpdatePassword(
        mixins.LoggedInOnlyView, mixins.EmailLoginOnlyView,
        SuccessMessageMixin, PasswordChangeView):
    template_name = "users/update-password.html"
    success_message = "Password successfully updated!"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        print(form)
        form.fields['old_password'].widget.attrs = {
            "placeholder": "Old Password"
        }
        form.fields['new_password1'].widget.attrs = {
            "placeholder": "New Password"
        }
        form.fields['new_password2'].widget.attrs = {
            "placeholder": "Confirm your new password"
        }
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()


@login_required
def switch_hosting(request):
    try:
        del request.session['is_hosting']
    except KeyError:
        request.session['is_hosting'] = True
    return redirect(reverse("core:home"))


def switch_lang(request):
    lang = request.GET.get("lang", 'en')
    if lang is not None:
        response = HttpResponse(200)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)

    return response


@login_required
def conversations(request):
    user = models.User.objects.get(pk=request.user.pk)
    conversations = user.conversations.order_by("-updated")
    return render(request, "users/conversations.html", {"conversations": conversations})
