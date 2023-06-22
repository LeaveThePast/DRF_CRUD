from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from logistic.models import Product, Stock
from logistic.serializers import ProductSerializer, StockSerializer, ProductSearchSerializer, PaginationSerializer, \
    StockSearchSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())
        search = request.query_params.get('search', None)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
            serializer = ProductSearchSerializer(qs, many=True)
            return Response(serializer.data)
        else:
            paginator = Paginator(qs, 10)
            page = request.query_params.get('page')
            data = paginator.get_page(page or 1)
            serializer = self.get_serializer(data, many=True)
            pagination_serializer = PaginationSerializer({
                'next_page': data.next_page_number() if data.has_next() else None,
                'prev_page': data.previous_page_number() if data.has_previous() else None,
                'count': paginator.count,
                'page_size': data.paginator.per_page,
                'results': serializer.data
            })
            return Response(pagination_serializer.data)


class StockViewSet(ModelViewSet):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()

    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())
        product_id = request.query_params.get('product_id', None)
        if product_id:
            qs = qs.filter(positions__product=product_id).distinct()
            serializer = StockSearchSerializer(qs, many=True)
            return Response(serializer.data)
        else:
            paginator = Paginator(qs, 10)
            page = request.query_params.get('page')
            data = paginator.get_page(page or 1)
            serializer = self.get_serializer(data, many=True)
            pagination_serializer = PaginationSerializer({
                'next_page': data.next_page_number() if data.has_next() else None,
                'prev_page': data.previous_page_number() if data.has_previous() else None,
                'count': paginator.count,
                'page_size': data.paginator.per_page,
                'results': serializer.data
            })
            return Response(pagination_serializer.data)
