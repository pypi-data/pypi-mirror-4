from django.utils import simplejson
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test

from .forms import LoginForm


def log_in(request, form):
    form = LoginForm(form)
    success = False
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'],
            password=form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                success = True

    return simplejson.dumps({
        'success': success
    })
