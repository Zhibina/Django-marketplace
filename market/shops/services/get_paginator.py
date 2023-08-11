from django.core.paginator import Paginator
from site_settings.models import SiteSettings


def get_paginator(query, page_number):
    site_settings = SiteSettings.load()
    paginator = Paginator(query, site_settings.pagination_size)
    page_obj = paginator.get_page(page_number)
    return page_obj
