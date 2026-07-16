from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # ============== FBVs ===============

    # path('products/', views.product_list),
    # path('products/create/', views.product_create),
    # path('products/<int:pk>/', views.product_detail),
    # path('orders/', views.order_list),
    # path('user-orders/', views.user_order_list),
    # path('products/info/', views.product_info),

    # ============== CBVs ===============

    # --- CBVs.Generics.urls:
    # path('users', views.UserListView.as_view()),
    # path('products/', views.ProductListCreateAPIView.as_view()),
    # path('products/<int:product_id>/', views.ProductDetailAPIView.as_view(), name='product_detail'),
    # path('products/info/', views.ProductInfoAPIView.as_view()),
    # path('Admin/orders/', views.AdminOrderListAPIView.as_view()),
    # path('orders/', views.OrderListAPIView.as_view(), name='user-orders'),
    # path('orders/<uuid:pk>/', views.OrderDetailAPIView.as_view()),
]

# --- CBVs.Viewsets.urls:

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('orders', views.OrdersViewSet, basename='orders')
router.register('products', views.ProductViewSet, basename='products')
urlpatterns += router.urls
