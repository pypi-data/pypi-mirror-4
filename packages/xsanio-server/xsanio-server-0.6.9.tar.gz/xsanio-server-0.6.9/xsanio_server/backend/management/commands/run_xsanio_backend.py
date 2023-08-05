from django.core.management.base import BaseCommand, CommandError
from backend import xsanio_backend

class Command(BaseCommand):
    help = 'Runs the server backend process'

    def handle(self, *args, **options):
        xsanio_backend.main()