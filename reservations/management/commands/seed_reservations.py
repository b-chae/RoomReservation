import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django_seed import Seed
from users import models as user_models
from rooms import models as room_models
from reservations.models import Reservation


class Command(BaseCommand):

    help = 'This command creates random reservations'

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", default=1, type=int,
            help="How many reservations do you want me to create?")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        guests = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()

        seeder.add_entity(Reservation, number, {
            'guest': lambda x: random.choice(guests),
            'room': lambda x: random.choice(rooms),
            'check_in': lambda x: datetime.now()
            + timedelta(days=random.randint(1, 10)),
            'check_out': lambda x: datetime.now()
            + timedelta(days=random.randint(11, 25)),
        })

        seeder.execute()

        self.stdout.write(self.style.SUCCESS(
            f"{number} reservations created!"))
