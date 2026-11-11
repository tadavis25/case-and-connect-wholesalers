from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('why-us/', views.why_us, name='why_us'),
    path('my-account/', views.my_account, name='my_account'),
]
