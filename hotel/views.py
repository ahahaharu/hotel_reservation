from django.shortcuts import render
from django.http import HttpResponse
from .models import Article, CompanyInfo, FAQ, Staff, Vacancy, Review, PromoCode

def home(request):
    latest_article = Article.objects.filter(is_published=True).order_by('-published_date').first()
    return render(request, 'hotel/home.html', {'latest_article': latest_article})

def about(request):
    company_info = CompanyInfo.objects.first()
    return render(request, 'hotel/about.html', {'company_info': company_info})

def news(request):
    articles = Article.objects.filter(is_published=True).order_by('-published_date')
    return render(request, 'hotel/news.html', {'articles': articles})

def glossary(request):
    faqs = FAQ.objects.all().order_by('order')
    return render(request, 'hotel/glossary.html', {'faqs': faqs})

def contacts(request):
    staff = Staff.objects.all().order_by('order')
    return render(request, 'hotel/contacts.html', {'staff': staff})

def privacy_policy(request):
    return render(request, 'hotel/privacy_policy.html')

def vacancies(request):
    active_vacancies = Vacancy.objects.filter(is_active=True).order_by('-date_posted')
    return render(request, 'hotel/vacancies.html', {'vacancies': active_vacancies})

def reviews(request):
    published_reviews = Review.objects.filter(is_published=True).order_by('-date_posted')
    return render(request, 'hotel/reviews.html', {'reviews': published_reviews})

def promo_codes(request):
    active_codes = PromoCode.objects.filter(is_active=True).order_by('valid_to')
    expired_codes = PromoCode.objects.filter(is_active=False).order_by('-valid_to')
    return render(request, 'hotel/promo_codes.html', {'active_codes': active_codes, 'expired_codes': expired_codes})