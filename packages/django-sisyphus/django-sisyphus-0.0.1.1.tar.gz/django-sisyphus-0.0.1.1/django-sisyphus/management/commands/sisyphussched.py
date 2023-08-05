from django.core.management.base import BaseCommand, CommandError
import sys
from sisyphus.bin.commands import scheduler


class Command(BaseCommand):
	args = '<imports>'
	help = """Run sisyphus scheduler."""

	def handle(self, *args, **kwargs):
		if not len(args):
			raise CommandError("No imports passed.")
		scheduler(args[0])
