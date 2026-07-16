from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from api.models import Product, Order
from api.seiralizers import ProductSerializer, OrderSerializer, ProductInfoSerializer
from api.filters import ProductFilter



@api_view(['GET'])
def product_list(request):
    queryset = Product.objects.all()
    product_filter = ProductFilter(request.GET, queryset=queryset)
    # CBVs اذا اردت تفعيل نظام البحث والترتيب لن يعمل النظام الذي عملناه في ال
    # لذا سنستخدم الطريقة العادية
    # SearchFilter
    query = request.GET.get('search')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)|
            Q(description__icontains=query)
        )
    # OrderFilter
    ordering = request.GET.get('ordering')
    if ordering:
        queryset = queryset.order_by(ordering)
    serializer = ProductSerializer(product_filter.qs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def product_create(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def product_detail(request, pk):
    product = get_object_or_404(Product,pk=pk)
    permission = AllowAny()
    if request.method in ['PUT', 'PATCH', 'DELETE']:
        permission = IsAdminUser()
    allowed = permission.has_permission(request, product_detail)
    if not allowed:
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    elif request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def order_list(request):
    orders = Order.objects.prefetch_related('items__product')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_order_list(request):
    orders = Order.objects.prefetch_related('items__product').filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    data = {
        'products' : products,
        'count': products.count(),
        'max_price': products.aggregate(max_price=Max('price'))['max_price']
    }
    serializer = ProductInfoSerializer(data)
    return Response(serializer.data)
