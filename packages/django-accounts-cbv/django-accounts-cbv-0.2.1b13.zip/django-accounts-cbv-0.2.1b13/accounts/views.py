from .forms import UserForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.http import base36_to_int
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
#from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView
import urlparse


class Login(FormView):
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'accounts/login.html'

    def get_success_url(self):
        redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')
        netloc = urlparse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        elif netloc and netloc != self.request.get_host():
            redirect_to = settings.LOGIN_REDIRECT_URL
        return redirect_to

    def form_valid(self, form):
        login(self.request, form.get_user())

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return super(Login, self).form_valid(form)

    #@method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(Login, self).dispatch(*args, **kwargs)


class Logout(RedirectView):
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_redirect_url(self):
        redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')
        if redirect_to:
            netloc = urlparse.urlparse(redirect_to)[1]
            if netloc and netloc != self.request.get_host():
                redirect_to = ''
        return redirect_to or '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, u'You have been logged out.')
        return super(Logout, self).get(request, *args, **kwargs)


class PasswordReset(FormView):
    form_class = PasswordResetForm
    token_generator = default_token_generator
    template_name = 'accounts/password_reset_form.html'
    email_template_name='accounts/password_reset_email.html'
    subject_template_name='accounts/password_reset_subject.txt'
    from_email = None
    success_url = '/'

    def form_valid(self, form):
        form.save(use_https=self.request.is_secure(),
                  token_generator=self.token_generator,
                  from_email=self.from_email,
                  email_template_name=self.email_template_name,
                  subject_template_name=self.subject_template_name,
                  request=self.request)
        messages.success(self.request, u'Check your email for the password reset link.')
        return super(PasswordReset, self).form_valid(form)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(PasswordReset, self).dispatch(*args, **kwargs)


class PasswordResetConfirm(FormView):
    form_class = SetPasswordForm
    token_generator = default_token_generator
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('home')

    def get_user(self, uid=None):
        if not hasattr(self, '_user'):
            if uid is None:
                uidb36 = self.kwargs.get('uidb36', 0)
                uid = base36_to_int(uidb36)
            try:
                self._user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                self._user = None
        return self._user

    def get_form_kwargs(self):
        kwargs = super(PasswordResetConfirm, self).get_form_kwargs()
        kwargs['user'] = self.get_user()
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, u'Password reset.')
        return super(PasswordResetConfirm, self).form_valid(form)

    #@method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        uidb36 = kwargs.get('uidb36', 0)
        uid = base36_to_int(uidb36)
        user = self.get_user(uid)
        token = kwargs.get('token', '')
        if self.token_generator.check_token(user, token):
            return super(PasswordResetConfirm, self).dispatch(*args, **kwargs)
        else:
            raise Http404


class UserUpdate(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'accounts/user_form.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, *args, **kwargs):
        messages.success(self.request, u'User account updated')
        return super(UserUpdate, self).form_valid(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserUpdate, self).dispatch(*args, **kwargs)
