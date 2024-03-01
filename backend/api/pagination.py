from rest_framework.pagination import PageNumberPagination

from api.constants import PAGE_SIZE


class LimitPageNumberPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
