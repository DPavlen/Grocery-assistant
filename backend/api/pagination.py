from rest_framework.pagination import PageNumberPagination

from core.constants import Lenght


class PaginationCust(PageNumberPagination):
    """Кастомная пагинация.
    page - номер страницы(integer).
    limit- количество объектов на странице(integer)."""
    page_size_query_param = 'limit'
    page_size = Lenght.PAGE_SIZE.value
