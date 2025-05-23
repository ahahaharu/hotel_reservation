from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'hotel'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('glossary/', views.glossary, name='glossary'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.add_review, name='reviews'),
    path('promo-codes/', views.promo_codes, name='promo_codes'),

    re_path(r'^rooms/$', views.RoomListView.as_view(), name='room_list'),
    re_path(r'^rooms/(?P<pk>\d+)/$', views.RoomDetailView.as_view(), name='room_detail'),
    re_path(r'^rooms/create/$', views.RoomCreateView.as_view(), name='room_create'),
    re_path(r'^rooms/(?P<pk>\d+)/update/$', views.RoomUpdateView.as_view(), name='room_update'),
    re_path(r'^rooms/(?P<pk>\d+)/delete/$', views.RoomDeleteView.as_view(), name='room_delete'),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('services/', views.services, name='services'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('visualizations/room-booking-distribution/', views.room_booking_distribution_chart, name='room_booking_distribution_chart'),
]