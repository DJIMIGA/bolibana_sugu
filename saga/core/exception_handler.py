import logging
from rest_framework.views import exception_handler


logger = logging.getLogger("cart.checkout")


def _safe_keys(data):
    if isinstance(data, dict):
        return list(data.keys())
    return None


def cart_exception_handler(exc, context):
    """
    Exception handler DRF pour tracer les erreurs 400 avant la vue.
    """
    request = context.get("request")
    if request and request.path == "/api/cart/checkout/":
        content_type = request.META.get("CONTENT_TYPE", "")
        user_id = getattr(getattr(request, "user", None), "id", None)
        body_size = 0
        try:
            body_size = len(request.body or b"")
        except Exception:
            body_size = 0

        data_keys = None
        try:
            data_keys = _safe_keys(getattr(request, "data", None))
        except Exception:
            data_keys = None

        logger.warning(
            "Checkout exception - user=%s path=%s content_type=%s body_size=%s data_keys=%s exc=%s",
            user_id,
            request.path,
            content_type,
            body_size,
            data_keys,
            exc,
        )

    return exception_handler(exc, context)
