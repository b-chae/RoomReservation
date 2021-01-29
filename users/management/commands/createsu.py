import random
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "This command creates superuser"

    def handle(self, *args, **options):
        try:
            User.objects.get(username="ebadmin")
        except User.DoesNotExist:
            User.objects.create_superuser(
                "ebadmin", "byol2chae@gmail.com", "12")
            self.stdout.write(self.style.SUCCESS('Super user created!'))
