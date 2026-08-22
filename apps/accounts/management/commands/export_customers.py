import csv
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = "Export customers to CSV."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        with open(options["path"], "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["email", "mobile_number", "first_name", "last_name", "account_status", "date_joined"])
            for user in User.objects.filter(role=User.Role.CUSTOMER).order_by("-date_joined"):
                writer.writerow([user.email, user.mobile_number, user.first_name, user.last_name, user.account_status, user.date_joined])
        self.stdout.write(self.style.SUCCESS(f"Exported customers to {options['path']}"))
