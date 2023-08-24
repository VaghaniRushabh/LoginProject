from django.urls import path, include
from users import views
from rest_framework.routers import DefaultRouter

app_name = 'users'

router = DefaultRouter()
router.register("", views.ApiViewSet, basename="session_auth")

urlpatterns = [
    path("", include(router.urls)),
]