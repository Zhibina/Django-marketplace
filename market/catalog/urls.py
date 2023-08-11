from django.conf import settings  # noqa F401
from django.urls import path
from django.views.decorators.cache import cache_page  # noqa F401

from catalog.views import ViewShows, CategoryCatalogView


app_name = "catalog"

urlpatterns = [
    # path("", cache_page(settings.CACHE_TIME_PER_DAY, key_prefix='catalog')(ViewShows.as_view()), name="show_product"),# noqa F401
    path("", ViewShows.as_view(), name="show_product"),
    # path("catalog_category/<slug:slug>/", cache_page(settings.CACHE_TIME_PER_DAY, key_prefix='catalog') # noqa F401
    #      (CategoryCatalogView.as_view()), name='catalog-category') # noqa F401
    path("catalog_category/<slug:slug>/", CategoryCatalogView.as_view(), name="catalog-category"),
]
