from rest_framework.response import Response
from django.db.models import Max
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination
from api.models import Product, Order, User
from api.filters import ProductFilter, OrderFilter, InStockFilterBackend
from api.tasks import send_order_confirmation_email
from api.seiralizers import (
    ProductSerializer, OrderSerializer, ProductInfoSerializer, OrderCreateSerializer, UserSerializer
)



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    throttle_scope = 'products'
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    pagination_class = None
    # pagination_class = PageNumberPagination
    # pagination_class.page_size = 3
    # pagination_class.page_query_param = 'pagenum' 
    # pagination_class.page_size_query_param = 'size'
    # pagination_class.max_page_size = 5 
    lookup_field = "id"
    lookup_url_kwarg = "product_id"
    
    
    @method_decorator(cache_page(60 * 15, key_prefix="product_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    '''
        يوجد طرق اكثر احترافية في عمل كاش لنظام المونتاجات واكثر امان واقل اخطاء 
        api/cache/Methods_Create_Cache.py راجع الملف 
    '''

    def get_permissions(self):
        admin_actions = ['create','update','partial_update','destroy','product_info']
        self.permission_classes = ([IsAdminUser] if self.action in admin_actions else [AllowAny])
        return super().get_permissions()

    @action(detail=False, methods=['GET'], url_path='info')
    def product_info(self, request):
        products = Product.objects.all()
        data = {
            'products' : products,
            'count': products.count(),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        }
        serializer = ProductInfoSerializer(data)
        return Response(serializer.data) 


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    # throttle_scope = 'orders'
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend] 

    @method_decorator(cache_page(60 * 30, key_prefix='order_list'))
    @method_decorator(vary_on_cookie) # JWT وليس على ال Cookies نضيفة في حال كان الموقع الخاص بنا يعتمد على ال 
    @method_decorator(vary_on_headers("Authorization")) # مع الكاش بشكل تلقائي , بمعنا انو ما الو داعي اضيفو هنا Headersفي الإصدارات الحديثة يتم اضافة ال
    def list(self, request, *args, **kwargs):           # ويمكن اضافة النوعين معا بالشكل السابق, وايضا موضوع الكاش هنا مع الطلبات مش ضروري كتير, فقط اعملناه لتعلم
        return super().list(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        send_order_confirmation_email.delay(order.order_id, self.request.user.email)
    
    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['POST', 'PATCH','PUT','DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)