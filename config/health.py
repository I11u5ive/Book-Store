from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        cache.set("health_check", "ok", timeout=10)

        if cache.get("health_check") != "ok":
            raise RuntimeError("Redis cache is unavailable")

    except Exception:
        return JsonResponse(
            {"status": "unhealthy"},
            status=503,
        )

    return JsonResponse({"status": "ok"})
