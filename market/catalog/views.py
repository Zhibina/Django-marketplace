from django.views import View

from catalog import services_views


class ViewShows(services_views.CatalogMixin, View):
    pass


class CategoryCatalogView(services_views.CatalogCategoryMixin, View):
    pass
