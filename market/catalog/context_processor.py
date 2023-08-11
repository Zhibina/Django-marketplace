from catalog.models import Catalog


def get_categories(request) -> dict:
    """Контекстный процессор для каталога и поиска товара"""
    search = request.GET.get("query")
    catalogs = Catalog.objects.all()
    if search:
        request.session.set_expiry(180)
        request.session["search"] = search
    return {"categories": catalogs}
