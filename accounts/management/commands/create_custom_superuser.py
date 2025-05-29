from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Creates a superuser with additional required fields'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'soham'
        email = 'botmartz@gmail.com'
        password = 'rdcv4c75'
        first_name = 'soham'
        last_name = 'sharma'

        try:
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_verified=True
                )
                self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
            else:
                self.stdout.write(self.style.WARNING('Superuser already exists.'))
        except IntegrityError:
            self.stdout.write(self.style.ERROR('Error creating superuser: User may already exist.'))