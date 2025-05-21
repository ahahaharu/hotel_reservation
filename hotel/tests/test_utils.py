from django.test import TestCase
from django.urls import reverse, resolve
from hotel.views import (
    home, about, news, glossary, contacts, 
    RoomListView, RoomDetailView, RegisterView, CustomLoginView
)

class UrlsTest(TestCase):
    def test_home_url(self):
        url = reverse('hotel:home')
        self.assertEqual(url, '/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, home)
    
    def test_about_url(self):
        url = reverse('hotel:about')
        self.assertEqual(url, '/about/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, about)
    
    def test_news_url(self):
        url = reverse('hotel:news')
        self.assertEqual(url, '/news/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, news)
    
    def test_glossary_url(self):
        url = reverse('hotel:glossary')
        self.assertEqual(url, '/glossary/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, glossary)
    
    def test_contacts_url(self):
        url = reverse('hotel:contacts')
        self.assertEqual(url, '/contacts/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, contacts)
    
    def test_room_list_url(self):
        url = reverse('hotel:room_list')
        self.assertEqual(url, '/rooms/')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, RoomListView)
    
    def test_room_detail_url(self):
        url = reverse('hotel:room_detail', args=[1])
        self.assertEqual(url, '/rooms/1/')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, RoomDetailView)
    
    def test_register_url(self):
        url = reverse('hotel:register')
        self.assertEqual(url, '/register/')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, RegisterView)
    
    def test_login_url(self):
        url = reverse('hotel:login')
        self.assertEqual(url, '/login/')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, CustomLoginView)