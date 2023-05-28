from . import views
from django.urls import path
from .views import contact, success

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),

    path('contact/', contact, name='contact'),
    path('success/', success, name='success'),

    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>', views.PostLike.as_view(), name='post_like'),
]