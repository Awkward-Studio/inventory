import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create a superuser if one does not exist"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "Atiq")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "atiqaxis7@gmail.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Zxcvbnm123")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' created successfully!")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already exists.")
            )
