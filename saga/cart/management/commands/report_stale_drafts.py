from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from cart.models import Order


class Command(BaseCommand):
    help = "Rapport des commandes en brouillon trop anciennes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=getattr(settings, "ORDER_DRAFT_STALE_DAYS", 7),
            help="Seuil en jours pour considérer un brouillon comme ancien",
        )

    def handle(self, *args, **options):
        days = options["days"]
        cutoff = timezone.now() - timedelta(days=days)
        stale_qs = (
            Order.objects.filter(status=Order.DRAFT, created_at__lt=cutoff)
            .select_related("user")
            .order_by("created_at")
        )

        total = stale_qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("Aucun brouillon ancien détecté."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"{total} brouillon(s) plus anciens que {days} jour(s)."
            )
        )

        for order in stale_qs:
            self.stdout.write(
                f"- order_id={order.id} order_number={order.order_number} "
                f"user_id={order.user_id} created_at={order.created_at.isoformat()} "
                f"total={order.total}"
            )
