from django.urls import path
from . import views

app_name = 'hotel'

urlpatterns = [
    # We'll add views later
    path('', views.home, name='home'),
]