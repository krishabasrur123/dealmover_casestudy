from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Financial_InfoViewSet
from . import views
# defines actual pages roots of my app


router= DefaultRouter()
router.register(r'extract', Financial_InfoViewSet)
urlpatterns=[
    path("api/", include(router.urls)),
]

