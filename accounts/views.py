from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.contrib.auth import logout

from .forms import UserRegisterForm, ProfileForm
from django.utils import timezone
from datetime import timedelta
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from actstream import action

from .models import Profile


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/profile.html', {'form': form})


class AccountDeleteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/delete_account.html')

    def post(self, request):
        if request.POST.get('confirm_delete') == 'DELETE':
            request.user.profile.account_deletion_requested = timezone.now()
            request.user.profile.save()
            action.send(request.user, verb='requested account deletion')
            messages.warning(request,
                             'Account deletion scheduled. Your account will be permanently deleted in 30 days.')
            logout(request)
            return redirect('home')
        return redirect('profile')


@login_required
def cancel_deletion(request):
    if request.user.profile.account_deletion_requested:
        request.user.profile.account_deletion_requested = None
        request.user.profile.save()
        action.send(request.user, verb='cancelled account deletion')
        messages.success(request, 'Account deletion cancelled.')
    return redirect('profile')


@login_required
def setup_2fa(request):
    if request.method == 'POST':
        device = TOTPDevice.objects.create(user=request.user, confirmed=False)
        url = device.config_url
        backup_codes = request.user.profile.generate_backup_codes()
        action.send(request.user, verb='enabled two-factor authentication')
        return render(request, 'accounts/setup_2fa.html', {
            'qr_code': url,
            'backup_codes': backup_codes
        })
    return render(request, 'accounts/setup_2fa.html')


@login_required
def disable_2fa(request):
    if request.method == 'POST':
        for device in devices_for_user(request.user):
            device.delete()
        request.user.profile.two_factor_enabled = False
        request.user.profile.save()
        action.send(request.user, verb='disabled two-factor authentication')
        messages.success(request, 'Two-factor authentication disabled.')
    return redirect('profile')