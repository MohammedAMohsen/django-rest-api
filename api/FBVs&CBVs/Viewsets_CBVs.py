from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Max
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from api.models import Product, Order
from api.seiralizers import ProductSerializer, OrderSerializer, ProductInfoSerializer
from api.filters import ProductFilter, OrderFilter, InStockFilterBackend


''' 
    CBVs.Viewsets:
    -- Default add system CRUD Automatically.
    -- Default add endpoint details (RetrieveAPIView) Automatically.
'''

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 3
    pagination_class.page_query_param = 'pagenum' 
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 5 

    def get_permissions(self):
        admin_actions = ['create','update','partial_update','destroy','info']
        self.permission_classes = ([IsAdminUser] if self.action in admin_actions else [AllowAny])
        return super().get_permissions()

    @action(detail=False, methods=['GET'], url_path='info', url_name='info')
    def product_info(self, request):
        products = Product.objects.all()
        data = {
            'products' : products,
            'count': products.count(),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        }
        serializer = ProductInfoSerializer(data)
        return Response(serializer.data)    


class OrdersViewSet(viewsets.ModelViewSet):  # هنا ReadOnlyModelViewSet في الحقيقة الأفضل استخدام نظام 
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend] 
    
    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['POST', 'PATCH','PUT','DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return super().get_queryset().filter(user=self.request.user)
        return super().get_queryset()
