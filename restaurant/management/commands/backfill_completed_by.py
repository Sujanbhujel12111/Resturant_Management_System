from django.core.management.base import BaseCommand
from django.db.models import Q
from restaurant.models import OrderHistory, OrderHistoryPayment, Payment
import csv
from datetime import timedelta

class Command(BaseCommand):
    help = 'Backfill OrderHistory.completed_by using Payment.edited_by by matching transaction_id or amount/date heuristics.'

    def add_arguments(self, parser):
        parser.add_argument('--export-csv', type=str, help='Path to export unmatched OrderHistory rows and their payments as CSV')
        parser.add_argument('--dry-run', action='store_true', help='Do not write updates, only report')
        parser.add_argument('--date-window-days', type=int, default=7, help='Date window (days) to consider when matching by date proximity')

    def handle(self, *args, **options):
        updated = 0
        tried = 0
        self.stdout.write('Starting backfill for OrderHistory.completed_by')

        # Iterate over histories missing completed_by
        qs = OrderHistory.objects.filter(completed_by__isnull=True)
        unmatched = []
        for oh in qs:
            tried += 1
            filled = False
            # 1) Try to match by transaction_id present in OrderHistoryPayment
            for ohp in oh.payments.all():
                tx = (ohp.transaction_id or '').strip()
                if tx:
                    p = Payment.objects.filter(transaction_id=tx).first()
                    if p and p.edited_by:
                        oh.completed_by = p.edited_by
                        oh.save(update_fields=['completed_by'])
                        updated += 1
                        filled = True
                        self.stdout.write(self.style.SUCCESS(f'Filled OrderHistory {oh.pk} from Payment tx {tx} -> {p.edited_by}'))
                        break
            if filled:
                continue

            # 2) Try to match by amount and date proximity: find any Payment with same amount around created_at
            for ohp in oh.payments.all():
                amount = ohp.amount
                if amount is None:
                    continue
                # payments on original orders may have similar amount and date
                possible = Payment.objects.filter(amount=amount).order_by('date_edited')
                # pick the closest by date if exists
                best = None
                best_delta = None
                for p in possible:
                    if not p.edited_by:
                        continue
                    # some Payment models have no timestamp or different field names; we use date_edited if available
                    try:
                        p_time = getattr(p, 'date_edited', None) or getattr(p, 'date_added', None) or None
                        if p_time and oh.created_at:
                            delta = abs((p_time - oh.created_at).total_seconds())
                            if best_delta is None or delta < best_delta:
                                best_delta = delta
                                best = p
                    except Exception:
                        continue
                if best and best.edited_by:
                    if not options.get('dry_run'):
                        oh.completed_by = best.edited_by
                        oh.save(update_fields=['completed_by'])
                    updated += 1
                    filled = True
                    self.stdout.write(self.style.SUCCESS(f'Filled OrderHistory {oh.pk} by amount match -> {best.edited_by}'))
                    break

            if not filled:
                # collect info for CSV/export so user can map manually
                payments_info = []
                for ohp in oh.payments.all():
                    payments_info.append({
                        'id': ohp.pk,
                        'amount': str(ohp.amount),
                        'transaction_id': ohp.transaction_id,
                        'date_added': ohp.date_added.isoformat() if getattr(ohp, 'date_added', None) else '',
                        'payment_method': ohp.payment_method,
                    })
                unmatched.append({
                    'orderhistory_pk': oh.pk,
                    'order_id': getattr(oh, 'order_id', None),
                    'created_at': oh.created_at.isoformat() if getattr(oh, 'created_at', None) else '',
                    'total_amount': str(getattr(oh, 'total_amount', '')),
                    'payments': payments_info,
                })

        # export unmatched if requested
        export_path = options.get('export_csv')
        if export_path:
            # flatten and write CSV with one line per payment (or empty payment row)
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['orderhistory_pk', 'order_id', 'created_at', 'total_amount', 'payment_id', 'payment_method', 'payment_amount', 'payment_tx', 'payment_date_added']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for u in unmatched:
                    if u['payments']:
                        for p in u['payments']:
                            writer.writerow({
                                'orderhistory_pk': u['orderhistory_pk'],
                                'order_id': u['order_id'],
                                'created_at': u['created_at'],
                                'total_amount': u['total_amount'],
                                'payment_id': p.get('id'),
                                'payment_method': p.get('payment_method'),
                                'payment_amount': p.get('amount'),
                                'payment_tx': p.get('transaction_id'),
                                'payment_date_added': p.get('date_added'),
                            })
                    else:
                        writer.writerow({
                            'orderhistory_pk': u['orderhistory_pk'],
                            'order_id': u['order_id'],
                            'created_at': u['created_at'],
                            'total_amount': u['total_amount'],
                            'payment_id': '',
                            'payment_method': '',
                            'payment_amount': '',
                            'payment_tx': '',
                            'payment_date_added': '',
                        })
            self.stdout.write(self.style.SUCCESS(f'Unmatched OrderHistory rows exported to {export_path} (rows: {len(unmatched)})'))

        self.stdout.write(self.style.SUCCESS(f'Backfill complete: tried {tried}, updated {updated}'))