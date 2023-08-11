from django.core.cache import cache
from django.http import JsonResponse


def clear_all_cache_view(request):
    """Очистка всего кеша"""
    cache.clear()
    return JsonResponse({'status': 'ok'})
