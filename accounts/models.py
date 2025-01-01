from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    account_deletion_requested = models.DateTimeField(null=True, blank=True)

    def generate_backup_codes(self):
        import random
        import string

        codes = []
        for _ in range(8):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append(code)
        self.backup_codes = codes
        self.save()
        return codes

    def __str__(self):
        return f'{self.user.username} Profile'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()