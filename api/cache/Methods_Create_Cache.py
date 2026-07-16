from rest_framework.response import Response
from rest_framework import viewsets
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from api.models import Product
from django.core.cache import cache
from urllib.parse import urlencode
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from api.models import Product
from api.seiralizers import ProductSerializer


# ===================================================
# Signals.py:
# -----------

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Remove all cached product lists.
    """

    cache.delete_pattern("products:*")

    print("Product cache cleared.")

# ===================================================
# Cache Strategy #1
# -----------------

class ProductViewSet(viewsets.ModelViewSet):
    """
    =====================================================
    Cache Strategy #1
    -----------------
    Cache the entire HTTP Response.

    Advantages:
        ✔ Very easy.
        ✔ One line of code.
        ✔ Supports:
            - django-filter
            - SearchFilter
            - OrderingFilter
            - Pagination
        automatically.

    Disadvantages:
        ✖ Caches the entire response.
        ✖ Not suitable when the page contains:
            - Logged-in user info
            - CSRF Tokens
            - Browsable API forms
            - Dynamic UI

    Best For:
        - Public APIs
        - Static pages
        - Blog
        - Documentation
    =====================================================
    """

    queryset = Product.objects.order_by("pk")
    serializer_class = ProductSerializer

    @method_decorator(cache_page(60 * 15, key_prefix="product_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# ====================================================================================================
# Cache Strategy #2
# -----------------


class ProductViewSet(viewsets.ModelViewSet):
    """
    =====================================================
    Cache Strategy #2
    -----------------
    Manual Redis Cache.

    Cache only serializer.data.

    Advantages:
        ✔ Safe.
        ✔ Doesn't cache HTML.
        ✔ Doesn't cache logged-in user data.

    Disadvantages:
        ✖ Does NOT support:
            - Search
            - Ordering
            - django-filter
            - Pagination

        because all requests use one cache key.

    Best For:
        - Learning
        - Small APIs
        - Endpoints with fixed output
    =====================================================
    """

    queryset = Product.objects.order_by("pk")
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        cache_key = "products"
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            print("Redis")
            return Response(cached_response)
        print("Database")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=900)
        return response    


# =======================================================================================
# Cache Strategy #3 (Recommended):
# ---------------------------------


class ProductViewSet(viewsets.ModelViewSet):
    """
    =====================================================
    Cache Strategy #3 (Recommended)
    -------------------------------
    Professional Redis Cache.

    Cache serializer.data only.

    Supports:
        ✔ django-filter
        ✔ SearchFilter
        ✔ OrderingFilter
        ✔ Pagination

    Cache key depends on URL query parameters.

    Example:

        /products/
            ↓
        products:

        /products/?search=iphone
            ↓
        products:search=iphone

        /products/?ordering=-price
            ↓
        products:ordering=-price

        /products/?page=2
            ↓
        products:page=2

        /products/?search=iphone&page=2
            ↓
        products:page=2&search=iphone

    This is a production-ready approach.
    =====================================================
    """
    queryset = Product.objects.order_by("pk")
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        # Build cache key from query parameters
        params = sorted(request.query_params.items())
        cache_key = "products:" + urlencode(params)
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            print("Redis")
            return Response(cached_response)
        print("Database")
        # Let DRF perform:
        #   - filtering
        #   - searching
        #   - ordering
        #   - pagination
        #   - serialization
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=900)
        return response
