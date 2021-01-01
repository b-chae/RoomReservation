import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from users import models as user_models
from rooms import models as room_models
from lists.models import List


class Command(BaseCommand):

    help = 'This command creates random lists'

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", default=1, type=int,
            help="How many lists do you want me to create?")

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        users = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()
        seeder.add_entity(List, number, {
            'user': lambda x: random.choice(users),
        })
        created = seeder.execute()
        cleaned = flatten(list(created.values()))
        for pk in cleaned:
            list_model = List.objects.get(pk=pk)
            for i in range(random.randint(1, 10)):
                list_model.rooms.add(random.choice(rooms))

        self.stdout.write(self.style.SUCCESS(f"{number} lists created!"))
