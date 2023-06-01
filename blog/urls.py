from . import views
from django.urls import path
from .views import contact, success

urlpatterns = [
    path('blog/', views.PostList.as_view(), name='blog'),

    path('contact/', contact, name='contact'),
    path('success/', success, name='success'),
    path('about/', views.about, name='about'),
    path('onlinetime/', views.onlinetime, name='onlinetime'),
    path('', views.home, name='home'),

    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>', views.PostLike.as_view(), name='post_like'),
]