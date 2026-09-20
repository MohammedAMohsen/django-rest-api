# مرجع شامل: أنماط الـ Views بـ Django REST Framework

> ملف مرجعي للرجوع إليه عند بناء أي `views.py` بمشروع DRF جديد.
> مبني على مراجعة مشروع `Course_DRF_Core`، مع إضافات (خصوصاً قسم الـ Mixins المخصصة) لتغطية الفجوات.

---

## جدول المحتويات

1. [الخريطة العامة: 4 مستويات](#1-الخريطة-العامة)
2. [FBV — `@api_view`](#2-fbv)
3. [`APIView` الخام](#3-apiview-الخام)
4. [Generic CBVs الجاهزة](#4-generic-cbvs-الجاهزة)
5. [Mixins — التركيبة الداخلية لكل Generic View](#5-mixins)
6. [بناء Mixin مخصص من الصفر](#6-mixin-مخصص)
7. [ViewSets + Routers + `@action`](#7-viewsets)
8. [جدول القرار السريع](#8-جدول-القرار)
9. [Cheat Sheet: كل الـ Generic Views المتاحة](#9-cheat-sheet)
10. [أمثلة جاهزة للنسخ](#10-أمثلة-جاهزة)

---

## 1. الخريطة العامة

DRF يقدّم 4 "مستويات" لبناء أي view، من الأكثر يدوية للأكثر جاهزية:

```
FBV (@api_view)  →  APIView خام  →  Generic CBV (Mixins جاهزة)  →  ViewSet (+ Router)
     الأكثر تحكماً                                              الأقل كود، الأكثر توحيداً
```

كل مستوى **مبني فوق اللي قبله** — `ViewSet` نفسه بالنهاية يستخدم نفس `APIView` كأساس، فقط بطبقات تنظيم إضافية فوقه.

---

## 2. FBV — `@api_view`

### الصيغة الأساسية

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### النقاط المهمة

| العنصر | الشرح |
|---|---|
| `@api_view([...])` | إجباري. يحدد HTTP methods المسموحة. أي method غير مذكورة → `405` تلقائياً. |
| `request.data` | بديل `request.POST` — يفهم JSON/form-data/multipart تلقائياً. |
| `Response(...)` | بديل `HttpResponse`/`render` — يتفاوض على الصيغة (JSON أو Browsable API HTML). |
| `@permission_classes([...])` | ديكوريتور إضافي لتحديد صلاحيات — لكنه **يطبّق نفس الصلاحية على كل methods بالدالة**. |

### صلاحيات مختلفة حسب method (بدون ديكوريتور جاهز)

```python
from rest_framework.permissions import AllowAny, IsAdminUser

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    permission = AllowAny() if request.method == 'GET' else IsAdminUser()
    if not permission.has_permission(request, product_detail):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    # ... باقي المنطق
```

### PUT مقابل PATCH — فرق جوهري

```python
serializer = ProductSerializer(product, data=request.data)                 # PUT: كل الحقول مطلوبة
serializer = ProductSerializer(product, data=request.data, partial=True)   # PATCH: تحديث جزئي
```

### متى تستخدم FBV؟

✅ Endpoint واحد بمنطق **خاص جداً وغير قياسي** (لا يشبه CRUD).
✅ نموذج ذهني بسيط — دالة عادية، منطق خطي واضح.
❌ **لا** لأي CRUD قياسي — الكود يتكرر بسرعة عبر عدة دوال منفصلة.

---

## 3. `APIView` الخام

الأساس الحقيقي لكل شيء بـ DRF. كل HTTP verb يصير **method مستقلة** بدل فحص `if` يدوي.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Max

class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        data = {
            'products': products,
            'count': products.count(),
            'max_price': products.aggregate(max_price=Max('price'))['max_price'],
        }
        serializer = ProductInfoSerializer(data)
        return Response(serializer.data)

    def post(self, request):
        # منطق مختلف تماماً لـ POST، بدون تشابك مع get()
        ...
```

### الفرق عن `@api_view`

| | `@api_view` | `APIView` |
|---|---|---|
| البنية | دالة + فروع `if method == ...` | class + method مستقلة لكل verb |
| مناسب لـ | endpoint بسيط، method واحدة أو اثنتين | منطق أكثر من method، كل واحدة معقدة لحالها |
| الصلاحيات | `@permission_classes([...])` أو يدوي | `permission_classes = [...]` كـ class attribute، أو `get_permissions()` |

### مثال بصلاحيات على مستوى الـ class

```python
class ProductInfoAPIView(APIView):
    permission_classes = [AllowAny]  # نفس الصلاحية لكل methods هنا

    def get(self, request):
        ...
```

### متى تستخدمه بدل FBV؟

✅ نفس حالات FBV (منطق خاص غير-CRUD)، لكن لما يكون فيه **أكثر من method** بمنطق منفصل واضح لكل واحدة — التنظيم كـ class methods أنظف من تكديس `if/elif` طويلة بدالة واحدة.

---

## 4. Generic CBVs الجاهزة

كل Generic View **جاهزة تحل عملية CRUD قياسية محددة**، عبر دمج `GenericAPIView` + Mixin/Mixins مناسبة (انظر القسم 5).

```python
from rest_framework import generics

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'   # بدل pk الافتراضية
    # lookup_field = 'slug'           # لو أردت البحث بحقل غير pk
```

### الـ Hooks الأساسية القابلة للـ Override (تنطبق على كل Generic View)

| Hook | الغرض | مثال استخدام |
|---|---|---|
| `get_queryset()` | تخصيص الـ queryset ديناميكياً (حسب المستخدم مثلاً) | `return super().get_queryset().filter(user=self.request.user)` |
| `get_serializer_class()` | serializer مختلف حسب الحالة | `if self.request.method == 'POST': return CreateSerializer` |
| `get_permissions()` | صلاحيات ديناميكية | راجع الأمثلة أعلاه |
| `perform_create(serializer)` | حقن بيانات إضافية عند الإنشاء | `serializer.save(user=self.request.user)` |
| `perform_update(serializer)` | نفس الفكرة عند التعديل | |
| `perform_destroy(instance)` | تخصيص منطق الحذف (soft-delete مثلاً) | `instance.is_active = False; instance.save()` |

### Pagination مخصص على مستوى view واحد

```python
from rest_framework.pagination import PageNumberPagination

class ProductListCreateAPIView(generics.ListCreateAPIView):
    ...
    pagination_class = PageNumberPagination
    pagination_class.page_size = 3
    pagination_class.page_query_param = 'pagenum'
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 5   # حد أقصى إجباري — مهم أمنياً/أدائياً
```

---

## 5. Mixins — التركيبة الداخلية لكل Generic View

### الفكرة الجوهرية

كل Generic View **ليست class مستقلة بذاتها** — هي **تركيبة (composition)** من:
- `GenericAPIView` (الأساس: يوفر `queryset`, `serializer_class`, `get_object()`, `get_queryset()`...)
- **زائد** واحد أو أكثر من الـ **Mixins** الجاهزة، كل وحدة تضيف **method واحدة محددة**.

### جدول: كل Mixin وماذا يضيف

| Mixin | يضيف method | يوفر عملية |
|---|---|---|
| `ListModelMixin` | `.list(request)` | `GET` لقائمة |
| `CreateModelMixin` | `.create(request)` | `POST` لإنشاء |
| `RetrieveModelMixin` | `.retrieve(request, pk)` | `GET` لعنصر واحد |
| `UpdateModelMixin` | `.update(request, pk)` + `.partial_update(...)` | `PUT`/`PATCH` |
| `DestroyModelMixin` | `.destroy(request, pk)` | `DELETE` |

### كيف تُبنى Generic Views الجاهزة فعلياً (المصدر الحقيقي بـ DRF)

هذا تقريباً الكود الفعلي بمصدر DRF نفسه (drf/generics.py):

```python
class ListCreateAPIView(mixins.ListModelMixin,mixins.CreateModelMixin,GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
```

**الدرس المهم:** `ListCreateAPIView` ليست "سحر" — هي فقط **دمج مُسبَّق** لـ mixins جاهزة + ربط كل HTTP verb بالـ method المناسبة. **أنت تقدر تسوي نفس هذا الدمج يدوياً** بأي تركيبة تحتاجها، وهذا بالضبط موضوع القسم القادم.

### متى تبني تركيبة مخصصة من الـ Mixins مباشرة (بدل الجاهزة)؟

لما تحتاج **تركيبة غير موجودة جاهزة**. مثال: تريد `List` + `Retrieve` فقط، بدون `Create`/`Update`/`Destroy` إطلاقاً (لا توجد Generic View جاهزة بهذا الاسم بالضبط):

```python
from rest_framework import mixins, generics

class ProductListRetrieveView(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)
```

---

## 6. بناء Mixin مخصص من الصفر

هذا الجزء **الأهم لتغطية الفجوة** — كيف تكتب Mixin **من عندك أنت**، مو بس تستخدم الجاهز من DRF.

### الفكرة

Mixin مخصص هو **class عادي فيه method أو أكثر**، مصمم ليُدمَج (`inherit`) مع views متعددة، لحل **مشكلة متكررة عبر أكثر من view** — بالضبط نفس فلسفة `AuthorRequiredMixin` اللي اقترحناها بمشروع `StudyRooms` (Django العادي)، بس هنا بسياق DRF.

### مثال 1: Mixin لتقييد الـ queryset حسب صاحب البيانات (نمط شائع جداً)

**المشكلة المتكررة:** عدة views مختلفة (Orders, Reviews, Notifications...) تحتاج نفس المنطق بالضبط: "المستخدم العادي يشوف بياناته فقط، الأدمن يشوف كل شيء".

```python
# api/mixins.py

class OwnerRestrictedQuerysetMixin:
    """
    Mixin يقيّد queryset تلقائياً على بيانات المستخدم الحالي،
    إلا لو كان staff (عندها يرى كل شيء).

    يتطلب: الموديل عنده حقل FK لـ User (افتراضياً 'user').
    """
    owner_field = 'user'   # قابل للتخصيص لكل view يستخدمه

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(**{self.owner_field: self.request.user})
```

**الاستخدام — نفس المنطق بأكثر من view بدون تكرار:**

```python
class OrderListAPIView(OwnerRestrictedQuerysetMixin, generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    # owner_field = 'user'  ← الافتراضي، لا حاجة لتكراره


class ReviewListAPIView(OwnerRestrictedQuerysetMixin, generics.ListAPIView):
    queryset = ReviewRating.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    owner_field = 'author'   # اسم الحقل مختلف هنا — Mixin يتكيف
```

**لاحظ ترتيب الوراثة:** الـ Mixin المخصص **دائماً يُكتب أولاً** (يسار)، والـ Generic View الأساسية **أخيراً** (يمين) — هذا يضمن أن Python's MRO (Method Resolution Order) يبحث أولاً عن `get_queryset()` بالـ Mixin المخصص قبل ما يصل للنسخة الافتراضية بـ `GenericAPIView`.

### مثال 2: Mixin لحقن بيانات تلقائياً عند الإنشاء

**المشكلة المتكررة:** أكثر من view يحتاج نفس نمط `perform_create(serializer.save(user=self.request.user))`.

```python
class AutoSetUserOnCreateMixin:
    """
    يعيّن المستخدم الحالي تلقائياً بحقل معين عند الإنشاء.
    """
    user_field = 'user'

    def perform_create(self, serializer):
        serializer.save(**{self.user_field: self.request.user})
```

```python
class OrderCreateAPIView(AutoSetUserOnCreateMixin, generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    # user_field = 'user' الافتراضي
```

### مثال 3: Mixin لتسجيل (logging) كل عملية حذف — Cross-cutting concern

```python
import logging
logger = logging.getLogger(__name__)

class LoggedDestroyMixin:
    """
    يسجّل بالـ logs أي عملية حذف، قبل تنفيذها فعلياً.
    مفيد للـ audit trail بأي موديل حساس (طلبات، مدفوعات...).
    """
    def perform_destroy(self, instance):
        logger.warning(
            f"User {self.request.user} is deleting {instance.__class__.__name__} #{instance.pk}"
        )
        super().perform_destroy(instance)
```

```python
class ProductDetailAPIView(LoggedDestroyMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
```

### القاعدة الذهبية لبناء Mixin مخصص

اسأل نفسك: **"هل هذا المنطق بالتحديد سيتكرر بأكثر من view واحد؟"**
- لو **نعم** → استخرجه لـ Mixin (حتى لو حالياً مستخدم بمكان واحد فقط، لكنك تتوقع تكراره قريباً).
- لو **لأ** (منطق خاص بـ view واحد فقط، ولن يتكرر) → اتركه مباشرة داخل الـ view نفسها (`get_queryset()` عادية) — Mixin لمنطق لن يتكرر هو تعقيد بدون فائدة حقيقية (over-engineering).

---

## 7. ViewSets + Routers + `@action`

### الفرق الجوهري عن Generic Views

| | Generic View | ViewSet |
|---|---|---|
| يمثّل | endpoint واحد | كل عمليات CRUD لموديل معًا |
| التسجيل بـ URLs | `path()` يدوي لكل view | تلقائي بالكامل عبر `Router` |
| فحص العملية الجارية | `self.request.method` | `self.action` (أدق دلالياً) |

### مثال كامل

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'product_id'

    def get_permissions(self):
        admin_actions = ['create', 'update', 'partial_update', 'destroy']
        self.permission_classes = [IsAdminUser] if self.action in admin_actions else [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=['GET'], url_path='info')
    def info(self, request):
        """ endpoint إضافي: GET /products/info/ """
        ...
        return Response(data)

    @action(detail=True, methods=['POST'], url_path='restock')
    def restock(self, request, product_id=None):
        """ endpoint إضافي على عنصر واحد: POST /products/<id>/restock/ """
        product = self.get_object()
        product.stock += int(request.data.get('quantity', 0))
        product.save(update_fields=['stock'])
        return Response({'stock': product.stock})
```

### `@action` — الوسائط المهمة

| الوسيط | المعنى |
|---|---|
| `detail=False` | يعمل على مستوى القائمة (`/products/info/`) |
| `detail=True` | يعمل على عنصر واحد (`/products/<id>/restock/`) — يستطيع استخدام `self.get_object()` |
| `methods=[...]` | HTTP methods المسموحة لهذا الـ action تحديداً |
| `url_path=` | الجزء النصي بالـ URL (افتراضياً = اسم الدالة) |
| `url_name=` | الاسم المستخدم بـ `reverse()` |

### تسجيل الـ Router

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')
urlpatterns = router.urls
```

يولّد تلقائياً: `list`, `create`, `retrieve`, `update`, `partial_update`, `destroy`, **وكل** `@action` معرَّفة — بدون كتابة أي `path()` يدوي.

### أنواع ViewSets الجاهزة

| Class | يوفر |
|---|---|
| `ModelViewSet` | كل الـ 6 عمليات (CRUD كامل) |
| `ReadOnlyModelViewSet` | فقط `list` + `retrieve` (مناسب لبيانات لا يجب تعديلها عبر API) |
| `ViewSet` (الخام) | فارغ تماماً — تكتب كل action يدوياً (`list`, `create`...) بنفسك |

---

## 8. جدول القرار السريع

| السؤال | الإجابة |
|---|---|
| Endpoint واحد، منطق خاص جداً، method واحدة أو اثنتين بسيطة | **FBV** (`@api_view`) |
| Endpoint واحد، منطق خاص، عدة methods معقدة كل واحدة لحالها | **`APIView`** الخام |
| عملية CRUD قياسية واحدة أو مجموعة صغيرة (List+Create فقط مثلاً) | **Generic CBV** المناسبة |
| نفس منطق (queryset تقييد، صلاحيات، إلخ) متكرر بعدة Generic Views | استخرجه لـ **Mixin مخصص** |
| موديل يحتاج مجموعة CRUD كاملة أو شبه كاملة | **ViewSet + Router** |
| تحتاج endpoint إضافي غير-CRUD ضمن نفس موارد الموديل | **`@action`** داخل ViewSet |

---

## 9. Cheat Sheet: كل الـ Generic Views المتاحة

| Class | العمليات | الاستخدام النموذجي |
|---|---|---|
| `ListAPIView` | `GET` (قائمة) فقط | قوائم قراءة فقط |
| `CreateAPIView` | `POST` فقط | إنشاء فقط، بدون عرض قائمة |
| `RetrieveAPIView` | `GET` (عنصر واحد) فقط | تفاصيل عنصر، قراءة فقط |
| `UpdateAPIView` | `PUT`/`PATCH` فقط | تعديل فقط |
| `DestroyAPIView` | `DELETE` فقط | حذف فقط |
| `ListCreateAPIView` | `GET` (قائمة) + `POST` | الأشيع لموارد بسيطة |
| `RetrieveUpdateAPIView` | `GET` + `PUT`/`PATCH` (عنصر واحد) | تعديل بدون حذف |
| `RetrieveDestroyAPIView` | `GET` + `DELETE` (عنصر واحد) | حذف بدون تعديل |
| `RetrieveUpdateDestroyAPIView` | `GET` + `PUT`/`PATCH` + `DELETE` | الأشيع لتفاصيل مورد كامل |

---

## 10. أمثلة جاهزة للنسخ

### نمط: صلاحيات ديناميكية حسب action (ViewSet)

```python
def get_permissions(self):
    if self.action in ['create', 'update', 'partial_update', 'destroy']:
        self.permission_classes = [IsAdminUser]
    else:
        self.permission_classes = [AllowAny]
    return super().get_permissions()
```

### نمط: serializer مختلف حسب العملية

```python
def get_serializer_class(self):
    if self.action in ['create', 'update', 'partial_update']:
        return OrderCreateSerializer
    return OrderSerializer
```

### نمط: تقييد queryset حسب المستخدم (بدون Mixin، مباشرة)

```python
def get_queryset(self):
    queryset = super().get_queryset()
    if self.request.user.is_staff:
        return queryset
    return queryset.filter(user=self.request.user)
```

### نمط: حقن بيانات إضافية عند الإنشاء + مهمة Celery غير متزامنة

```python
def perform_create(self, serializer):
    order = serializer.save(user=self.request.user)
    send_order_confirmation_email.delay(order.order_id, self.request.user.email)
```

### نمط: تجنّب N+1 Query دائماً مع Nested Serializers

```python
queryset = Order.objects.prefetch_related('items__product')   # ForeignKey متسلسل → prefetch_related
queryset = Product.objects.select_related('category')          # ForeignKey مباشر → select_related
```

---

## ملخص ذهني سريع

```
منطق خاص، endpoint واحد بسيط          → FBV
منطق خاص، عدة methods معقدة           → APIView خام
CRUD قياسي، عملية أو اثنتين           → Generic CBV
نفس المنطق متكرر بعدة Generic Views   → Mixin مخصص
CRUD كامل لموديل                       → ViewSet + Router
عملية إضافية غير-CRUD على نفس المورد   → @action
```
