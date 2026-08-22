import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Preview product CSV import and report validation errors without writing data."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        errors = []
        total = 0
        with open(options["path"], newline="", encoding="utf-8") as handle:
            for index, row in enumerate(csv.DictReader(handle), start=2):
                total += 1
                for field in ["sku", "name", "category", "mrp", "selling_price"]:
                    if not row.get(field):
                        errors.append(f"Row {index}: missing {field}")
                try:
                    Decimal(row.get("mrp", ""))
                    Decimal(row.get("selling_price", ""))
                except (InvalidOperation, TypeError):
                    errors.append(f"Row {index}: invalid price")
        self.stdout.write(f"Rows checked: {total}")
        if errors:
            for error in errors:
                self.stdout.write(self.style.ERROR(error))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("Preview passed."))
