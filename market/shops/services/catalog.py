from catalog.models import Catalog


def get_featured_categories():
    featured_categories = Catalog.objects.filter(is_featured=True)[:3]
    return featured_categories
