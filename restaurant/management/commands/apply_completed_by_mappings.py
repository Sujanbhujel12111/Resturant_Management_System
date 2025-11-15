from django.core.management.base import BaseCommand
import csv
from django.contrib.auth import get_user_model
from restaurant.models import OrderHistory


class Command(BaseCommand):
    help = 'Apply completed_by mappings from CSV. CSV must contain columns: orderhistory_pk,completed_by_username'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='Path to CSV file with mappings')
        parser.add_argument('--dry-run', action='store_true', help='Do not write updates, only report')

    def handle(self, *args, **options):
        csvfile = options['csvfile']
        dry_run = options.get('dry_run', False)
        User = get_user_model()

        tried = 0
        updated = 0
        errors = 0

        self.stdout.write(f"Reading mappings from {csvfile} (dry_run={dry_run})")
        with open(csvfile, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                tried += 1
                pk = (row.get('orderhistory_pk') or '').strip()
                username = (row.get('completed_by_username') or row.get('completed_by') or '').strip()
                if not pk or not username:
                    self.stdout.write(self.style.ERROR(f"Skipping row {tried}: missing pk or username: {row}"))
                    errors += 1
                    continue

                # Resolve user
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"User not found: '{username}' for row {tried}"))
                    errors += 1
                    continue

                # Resolve OrderHistory by pk or by order_id
                oh = None
                try:
                    if pk.isdigit():
                        oh = OrderHistory.objects.filter(pk=int(pk)).first()
                    if not oh:
                        # try by order_id if pk wasn't a numeric primary key
                        oh = OrderHistory.objects.filter(order_id=pk).first()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error finding OrderHistory for '{pk}': {e}"))
                    errors += 1
                    continue

                if not oh:
                    self.stdout.write(self.style.ERROR(f"OrderHistory not found for '{pk}' (row {tried})"))
                    errors += 1
                    continue

                # Apply mapping
                if dry_run:
                    self.stdout.write(self.style.WARNING(f"Dry-run: would set OrderHistory {oh.pk}.completed_by = {user.username}"))
                    updated += 0
                else:
                    oh.completed_by = user
                    oh.save(update_fields=['completed_by'])
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated OrderHistory {oh.pk}: completed_by -> {user.username}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Processed: {tried}, updated: {updated}, errors: {errors}"))
