# 🚀 Django REST Framework - Complete API Project

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.x-green?logo=django)
![Django REST Framework](https://img.shields.io/badge/DRF-3.16-red?logo=django)
![JWT](https://img.shields.io/badge/JWT-SimpleJWT-orange)
![Redis](https://img.shields.io/badge/Redis-Latest-red?logo=redis)
![Celery](https://img.shields.io/badge/Celery-Latest-brightgreen?logo=celery)
![Docker](https://img.shields.io/badge/Docker-Latest-blue?logo=docker)
![SQLite](https://img.shields.io/badge/SQLite-Development-blue?logo=sqlite)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.x-success)
![Swagger](https://img.shields.io/badge/Swagger-UI-green)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

---

# 📖 About

A complete **Django REST Framework** educational project covering the entire backend development workflow, from building REST APIs to implementing authentication, permissions, testing, caching, background tasks, API documentation, filtering, pagination, throttling, and much more.

This project was built as part of a comprehensive DRF learning journey and demonstrates how modern REST APIs are designed using Django and Django REST Framework.

---

# ✨ Features

## REST API Development

- Function-Based Views (FBVs)
- Class-Based Views (Generic Views)
- APIView
- GenericAPIView
- ViewSets
- ModelViewSet
- Routers
- Custom Actions

---

## CRUD Operations

Complete CRUD implementation for:

- Products
- Orders
- Order Items

Including:

- List
- Retrieve
- Create
- Update
- Partial Update
- Delete

---

## Authentication

Implemented multiple authentication mechanisms:

- Session Authentication
- JWT Authentication
- SimpleJWT

Including:

- Access Tokens
- Refresh Tokens
- Bearer Authentication

---

## Permissions

Role-based permissions using:

- AllowAny
- IsAuthenticated
- IsAdminUser

Custom permissions implemented through:

- `get_permissions()`
- Action-based permissions
- Method-based permissions

---

## Serialization

Implemented:

- ModelSerializer
- Nested Serializers
- Read-only fields
- SerializerMethodField
- Source fields
- Custom validation
- Serializer switching
- Nested object creation
- Nested object updates

---

## Query Optimization

Implemented:

- `select_related()`
- `prefetch_related()`
- Custom QuerySets

---

## Filtering

Using:

- django-filter

Features include:

- Exact lookup
- icontains lookup
- Range filtering
- Less than / Greater than
- Date filtering
- Custom FilterSets
- Custom Filter Backends

---

## Search

DRF SearchFilter

Supports searching across multiple fields.

---

## Ordering

OrderingFilter

Supports dynamic ordering by:

- Name
- Price
- Custom fields

---

## Pagination

Implemented:

- PageNumberPagination
- LimitOffsetPagination

Including:

- Custom page size
- Maximum page size
- Custom query parameters

---

## API Documentation

Using:

- drf-spectacular
- OpenAPI 3
- Swagger UI
- ReDoc

Automatically generated API documentation.

---

## JWT Authentication

Using:

- djangorestframework-simplejwt

Supports:

- Login
- Access Token
- Refresh Token
- Protected Endpoints

---

## Testing

Implemented:

- Django TestCase
- DRF APITestCase

Testing includes:

- Authentication
- Authorization
- CRUD
- Permissions
- API Responses

---

## Caching

Redis caching implemented for:

- Product listing
- Order listing

Including:

- cache_page()
- Cache invalidation
- Signals
- Vary Headers

---

## Redis

Redis is used for:

- Django Cache Backend
- Celery Broker
- Celery Result Backend

---

## Celery

Background task processing using Celery.

Implemented:

- Email tasks
- Order confirmation emails
- Redis Broker
- Worker processes

---

## Signals

Using Django Signals:

- post_save
- post_delete

To automatically invalidate cached data.

---

## Throttling

Implemented API Rate Limiting using:

- AnonRateThrottle
- UserRateThrottle
- ScopedRateThrottle
- Custom Throttle Classes

---

## Transactions

Database consistency using:

```python
transaction.atomic()
```

to ensure safe creation and updating of nested objects.

---

## Performance

Project includes several backend optimization techniques:

- Redis Cache
- Query Optimization
- Pagination
- Background Tasks
- API Throttling

---

# 🛠 Technologies Used

- Python
- Django
- Django REST Framework
- SimpleJWT
- Redis
- Celery
- Docker
- drf-spectacular
- django-filter
- SQLite

---

# 📂 Project Structure

```
core/
│
├── settings.py
├── urls.py
├── celery.py
│
api/
│
├── models.py
├── serializers.py
├── views.py
├── filters.py
├── throttles.py
├── tasks.py
├── signals.py
├── tests.py
├── urls.py
│
manage.py
README.md
```

---

# 🚀 Main DRF Concepts Covered

✔ Function Based Views

✔ APIView

✔ Generic Views

✔ ViewSets

✔ Routers

✔ Serializers

✔ Nested Serializers

✔ CRUD APIs

✔ JWT Authentication

✔ Permissions

✔ Filtering

✔ Searching

✔ Ordering

✔ Pagination

✔ Testing

✔ OpenAPI

✔ Swagger

✔ ReDoc

✔ Redis Cache

✔ Celery Tasks

✔ Background Jobs

✔ API Throttling

✔ Signals

✔ Transactions

✔ Query Optimization

---

# 📚 Learning Objectives

This project demonstrates how to build production-ready REST APIs using Django REST Framework while following modern backend development practices.

It serves as a practical reference covering nearly every essential DRF topic from beginner to advanced level.

---

# 📄 License

This project is licensed under the MIT License.