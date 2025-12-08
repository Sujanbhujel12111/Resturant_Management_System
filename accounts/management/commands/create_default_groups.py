from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = (
        "Create standard groups (kitchen, orders, menu, place_order, payments, reports) "
        "and attach suggested permissions when those permissions exist."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--assign-user",
            dest="assign_user",
            help="Username to assign all created groups to (optional)",
        )

    def handle(self, *args, **options):
        groups_map = {
            "kitchen": [
                ("restaurant", "order", ["change", "view"]),
                ("restaurant", "orderitem", ["view"]),
            ],
            "orders": [
                ("restaurant", "order", ["add", "change", "view"]),
                ("restaurant", "payment", ["add", "change", "view"]),
            ],
            "menu": [
                ("restaurant", "menuitem", ["add", "change", "view", "delete"]),
                ("restaurant", "category", ["add", "change", "view", "delete"]),
                ("products", "product", ["add", "change", "view", "delete"]),
            ],
            "place_order": [
                ("restaurant", "order", ["add", "view"]),
                ("restaurant", "payment", ["add", "view"]),
            ],
            "payments": [
                ("restaurant", "payment", ["view", "change"]),
            ],
            "reports": [
                ("restaurant", "order", ["view"]),
                ("restaurant", "payment", ["view"]),
            ],
        }

        for name, perms in groups_map.items():
            group, created = Group.objects.get_or_create(name=name)
            self.stdout.write(self.style.SUCCESS(f"Group '{name}': {'created' if created else 'exists'}"))

            for app_label, model, actions in perms:
                for action in actions:
                    codename = f"{action}_{model}"
                    qs = Permission.objects.filter(codename=codename, content_type__app_label=app_label)
                    if qs.exists():
                        for p in qs:
                            group.permissions.add(p)
                            self.stdout.write(f"  Added permission {p.codename} ({app_label}.{p.content_type.model})")
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"  Permission '{codename}' for app '{app_label}' not found; skipped."))

        assign_user = options.get("assign_user")
        if assign_user:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user = User.objects.get(username=assign_user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User '{assign_user}' not found; skipping assignment."))
            else:
                for gname in groups_map.keys():
                    g = Group.objects.get(name=gname)
                    user.groups.add(g)
                self.stdout.write(self.style.SUCCESS(f"Assigned groups to user '{user.username}'"))

        self.stdout.write(self.style.SUCCESS("Default groups creation complete."))
