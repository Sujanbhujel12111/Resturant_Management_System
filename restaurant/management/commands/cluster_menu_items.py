"""
Django management command to cluster menu items by demand using K-Means.
Usage: python manage.py cluster_menu_items
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
import numpy as np
from sklearn.cluster import KMeans
from restaurant.models import MenuItem, OrderHistoryItem


class Command(BaseCommand):
    help = 'Cluster menu items by demand using K-Means (High, Medium, Low tier)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--n-clusters',
            type=int,
            default=3,
            help='Number of clusters (tiers) to create. Default: 3'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed output'
        )

    def handle(self, *args, **options):
        n_clusters = options['n_clusters']
        verbose = options['verbose']

        self.stdout.write(self.style.SUCCESS('Starting K-Means clustering...'))

        # Step 1: Get order counts for all items from OrderHistory (completed orders only)
        try:
            item_order_counts = (
                OrderHistoryItem.objects
                .values('item__id', 'item__name')
                .annotate(order_count=Count('id'))
                .order_by('-order_count')
            )

            # Convert to list
            items_data = list(item_order_counts)

            if not items_data:
                self.stdout.write(
                    self.style.WARNING('No order history found. Run this command after orders exist.')
                )
                return

            if verbose:
                self.stdout.write(f'\nFound {len(items_data)} items with order history:')
                for item in items_data:
                    self.stdout.write(
                        f"  - {item['item__name']}: {item['order_count']} orders"
                    )

            # Step 2: Prepare data for K-Means
            order_counts = np.array([item['order_count'] for item in items_data]).reshape(-1, 1)

            # Step 3: Train K-Means
            if len(items_data) < n_clusters:
                self.stdout.write(
                    self.style.WARNING(
                        f'Only {len(items_data)} items found, but {n_clusters} clusters requested. '
                        f'Adjusting to {len(items_data)} clusters.'
                    )
                )
                n_clusters = len(items_data)

            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(order_counts)

            if verbose:
                self.stdout.write(f'\nCluster centers (order counts): {kmeans.cluster_centers_.flatten()}')

            # Step 4: Map clusters to tier names (highest cluster = highest demand)
            # Sort clusters by center value to assign tier names
            cluster_order = np.argsort(-kmeans.cluster_centers_.flatten())  # descending order
            cluster_to_tier = {}
            tier_names = []

            if n_clusters == 1:
                tier_names = ['high']
            elif n_clusters == 2:
                tier_names = ['high', 'low']
            elif n_clusters >= 3:
                tier_names = ['high', 'medium', 'low'] + ['low'] * (n_clusters - 3)

            for rank, cluster_id in enumerate(cluster_order):
                cluster_to_tier[cluster_id] = tier_names[min(rank, len(tier_names) - 1)]

            # Step 5: Update MenuItem with tier and order count
            updated_count = 0
            for item_data, cluster_label in zip(items_data, cluster_labels):
                menu_item = MenuItem.objects.get(id=item_data['item__id'])
                tier = cluster_to_tier[cluster_label]
                
                menu_item.demand_tier = tier
                menu_item.order_count = item_data['order_count']
                menu_item.last_tier_update = timezone.now()
                menu_item.save()
                updated_count += 1

                if verbose:
                    self.stdout.write(
                        f"  {menu_item.name}: {item_data['order_count']} orders → {tier.upper()}"
                    )

            # Step 6: Display summary by tier
            self.stdout.write(self.style.SUCCESS('\n✓ Clustering complete!'))
            self.stdout.write(f'\nUpdated {updated_count} menu items.\n')

            # Print tier summary
            for tier in ['high', 'medium', 'low']:
                count = MenuItem.objects.filter(demand_tier=tier).count()
                items_in_tier = MenuItem.objects.filter(demand_tier=tier).values_list(
                    'name', 'order_count'
                )
                self.stdout.write(self.style.SUCCESS(f'{tier.upper()} DEMAND (Tier {["high", "medium", "low"].index(tier) + 1}):'))
                if items_in_tier:
                    for name, order_count in items_in_tier:
                        self.stdout.write(f'  ├─ {name}: {order_count} orders')
                else:
                    self.stdout.write('  (no items)')
                self.stdout.write('')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during clustering: {str(e)}')
            )
            raise
