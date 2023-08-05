from django.core.management.base import BaseCommand, CommandError
from zeropass.models import Token

class Command(BaseCommand):
    help = 'deletes all expire zeropass tokens'


    def handle(self, *args, **options):
        expired_tokens = Token.objects.expired()
        expired_tokens.delete()

