from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta


class Command(BaseCommand):
    help = 'Deletes accounts that were scheduled for deletion 30 days ago'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(days=30)
        users = User.objects.filter(
            profile__account_deletion_requested__lte=threshold
        )
        count = users.count()
        users.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} expired accounts')
        )
