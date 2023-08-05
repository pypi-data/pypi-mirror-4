from django.core.management.base import BaseCommand, CommandError
import sys
from sisyphus.bin.commands import worker


class Command(BaseCommand):
	args = '<imports>'
	help = """Run sisyphus worker."""

	def handle(self, *args, **kwargs):
		if not len(args):
			raise CommandError("No imports passed.")
		worker(args[0])