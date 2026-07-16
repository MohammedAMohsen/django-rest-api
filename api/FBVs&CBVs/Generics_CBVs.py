from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import generics
from django.db.models import Max
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from api.models import Product, Order, User
from api.seiralizers import ProductSerializer, OrderSerializer, ProductInfoSerializer, UserSerializer
from api.filters import ProductFilter, InStockFilterBackend


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None


# List View Products & Create > Provides GET and POST handlers
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('pk') # لدواعي السلامة في العرض بسبب دخول نظام الصفحات order_by('pk') اضفنا 
    serializer_class = ProductSerializer

    # Filter, Search, Order
    # filterset_fields = ('name', 'price') # قمنا بتخصيص الفلتر في ملف خارجي filter.py لاعطاء مرونة في التصفية
    filterset_class = ProductFilter
    search_fields = ['name', 'description'] # '=name' <-- (exact) لو اردت تقييد البحث ليكون بالضبط
    ordering_fields = ['name', 'price']
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,   # <-- سيقوم بعمل فلتر تلقائي ويعرض فقط المونتجات التي متوفرة 
    ]

    # Pagination > لكامل المشورع Settingالإعداد الطبيعي تم في ملف ال 
    # لكن اذا اردت تخصيص الصفحات يصبح النظام ينظر لهذا الإعداد ويظل الأعداد الأصلي في حال ما وجد الإعداد المخصص هنا
    pagination_class = PageNumberPagination
    pagination_class.page_size = 3
    pagination_class.page_query_param = 'pagenum' # اذا اردت تغيير الإسم
    pagination_class.page_size_query_param = 'size' # اعطاء التحكم للمستخدم في ارجع كمية البيانات في الصفحة
    pagination_class.max_page_size = 5 # لضبط الكمية حتى لا يقوم المستخدم بجلب كل العناصر من قاعدة البيانات
    # http://127.0.0.1:8000/products/?size=3&pagenum=4 --> عنصرين في الصفحة والصفحة الرابعة

    # Override permissions
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


# View & Update & Delete > Single Product
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.filter(stock__gt=0) # field__lookup:
    serializer_class = ProductSerializer
    # في حال ما بدي اغير طريقة البحث pk القيمة الإفتراضية في البحث تكون عبر ال 
    # كالتالي lookup_url_kwarg لو اريدت التغيير اعين قيمة لل
    lookup_url_kwarg = 'product_id'  # <int:product_id> الى <int:pk> نغير القيمة من pathفي ال
    # كالتالي lookup_field لو بدي اجيب المونتج حسب اسمو نفس الخطوات السابقة بالضبط مع تغيير ال 
    # lookup_field = 'name' # --> filterبغير الحقل الحقيقي الي هستخدمو في عملية ال
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PATCH','PUT','DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class AdminOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]


class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    # للمميثود المسؤوالة عن شكل البيانات الي بعمل استعلام عليها Override هان عملت
    # self.request.user عشام من خلالها اقدر اوصل للستخدم الحالي 
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        data = {
            'products' : products,
            'count': products.count(),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        }
        serializer = ProductInfoSerializer(data)
        return Response(serializer.data)
