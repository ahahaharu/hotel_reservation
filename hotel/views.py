from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory

from .models import (
    Article, CompanyInfo, FAQ, Staff, Vacancy, Review, 
    PromoCode, Room, RoomCategory, RoomImage
)
from .forms import RoomForm, RoomImageForm

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

class RoomListView(ListView):
    model = Room
    template_name = 'hotel/room_list.html'
    context_object_name = 'rooms'
    ordering = ['room_number']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = RoomCategory.objects.all()
        return context

class RoomDetailView(DetailView):
    model = Room
    template_name = 'hotel/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# CREATE operation
class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'hotel/room_form.html'
    success_url = reverse_lazy('hotel:room_list')
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Room'
        
        # Add formset for room images
        if self.request.POST:
            context['image_formset'] = RoomImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = RoomImageFormSet()
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            self.object = form.save()
            
            # Save the formset with the room instance
            image_formset.instance = self.object
            image_formset.save()
            
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

# UPDATE operation
class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'hotel/room_form.html'
    context_object_name = 'room'
    login_url = '/admin/login/'
    
    def get_success_url(self):
        return reverse_lazy('hotel:room_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Room'
        
        # Add formset for room images
        if self.request.POST:
            context['image_formset'] = RoomImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['image_formset'] = RoomImageFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        if image_formset.is_valid():
            self.object = form.save()
            
            # Save the formset with the room instance
            image_formset.instance = self.object
            image_formset.save()
            
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

# DELETE operation
class RoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'hotel/room_confirm_delete.html'
    success_url = reverse_lazy('hotel:room_list')
    context_object_name = 'room'
    login_url = '/admin/login/'

# Initialize formset for room images
RoomImageFormSet = inlineformset_factory(
    Room, 
    RoomImage, 
    form=RoomImageForm, 
    extra=1, 
    can_delete=True
)