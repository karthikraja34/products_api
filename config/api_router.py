from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path(
        "v1/products/",
        include(("products_api.products.api.urls", "products"), namespace="products"),
    ),
    path(
        "v1/webhooks/",
        include(("products_api.webhooks.api.urls", "webhooks"), namespace="webhooks"),
    ),
]


app_name = "api"
urlpatterns += router.urls
