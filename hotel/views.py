from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import inlineformset_factory
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django import forms
from datetime import date, timedelta

from .models import (
    Article, CompanyInfo, FAQ, Staff, Vacancy, Review, 
    PromoCode, Room, RoomCategory, RoomImage, Reservation, Client
)
from .forms import RoomForm, RoomImageForm
from .auth_forms import UserRegisterForm, UserLoginForm, UserProfileForm

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
        context['is_staff'] = self.request.user.is_staff or self.request.user.is_superuser
        return context

class RoomDetailView(DetailView):
    model = Room
    template_name = 'hotel/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.request.user.is_staff or self.request.user.is_superuser
        return context

# CREATE operation
class RoomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'hotel/room_form.html'
    success_url = reverse_lazy('hotel:room_list')
    login_url = reverse_lazy('hotel:login')
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('hotel:room_list')
        return super().dispatch(request, *args, **kwargs)
    
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
    
    def test_func(self):
        return is_staff_user(self.request.user)

# UPDATE operation
class RoomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'hotel/room_form.html'
    context_object_name = 'room'
    login_url = reverse_lazy('hotel:login')
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('hotel:room_list')
        return super().dispatch(request, *args, **kwargs)
    
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
    
    def test_func(self):
        return is_staff_user(self.request.user)

# DELETE operation
class RoomDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Room
    template_name = 'hotel/room_confirm_delete.html'
    success_url = reverse_lazy('hotel:room_list')
    context_object_name = 'room'
    login_url = reverse_lazy('hotel:login')
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('hotel:room_list')
        return super().dispatch(request, *args, **kwargs)
    
    def test_func(self):
        return is_staff_user(self.request.user)

# Initialize formset for room images
RoomImageFormSet = inlineformset_factory(
    Room, 
    RoomImage, 
    form=RoomImageForm, 
    extra=1, 
    can_delete=True
)

# Add this helper function
def is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

# Add staff dashboard view
@login_required
@user_passes_test(is_staff_user)
def staff_dashboard(request):
    """Dashboard for staff members to view all reservations and clients"""
    recent_reservations = Reservation.objects.all().order_by('-created_at')[:10]
    all_clients = Client.objects.all().order_by('last_name', 'first_name')
    
    context = {
        'recent_reservations': recent_reservations,
        'clients': all_clients,
        'total_reservations': Reservation.objects.count(),
        'total_clients': Client.objects.count(),
    }
    
    return render(request, 'hotel/staff/dashboard.html', context)

# Add client dashboard view
@login_required
def client_dashboard(request):
    """Dashboard for clients to view their reservations"""
    try:
        client = request.user.client
        reservations = client.reservations.all().order_by('-created_at')
        
        context = {
            'client': client,
            'reservations': reservations,
        }
        
        return render(request, 'hotel/client/dashboard.html', context)
    except:
        # Handle case where user has no associated client profile
        messages.error(request, "Your account is not properly set up. Please contact support.")
        return redirect('hotel:home')

class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'hotel/auth/register.html'
    success_url = reverse_lazy('hotel:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your account has been created! You can now log in.')
        return response

class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'hotel/auth/login.html'
    
    def get_success_url(self):
        return reverse_lazy('hotel:home')

def logout_view(request):
    logout(request)
    return redirect('hotel:home')

@login_required
def profile_view(request):
    client = request.user.client
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('hotel:profile')
    else:
        form = UserProfileForm(instance=client)
    
    reservations = client.reservations.all().order_by('-check_in_date')
    reviews = client.reviews.all().order_by('-date_posted')
    
    context = {
        'form': form,
        'reservations': reservations,
        'reviews': reviews
    }
    
    return render(request, 'hotel/auth/profile.html', context)

# Add booking functionality
class BookingForm(forms.Form):
    check_in_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    check_out_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    special_requests = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in < date.today():
                raise forms.ValidationError("Check-in date cannot be in the past")
            
            if check_out <= check_in:
                raise forms.ValidationError("Check-out date must be after check-in date")
                
        return cleaned_data

@login_required
def book_room(request, room_id):
    """Allow a client to book a room"""
    room = get_object_or_404(Room, id=room_id)
    
    # Check if room is available
    if room.status != 'available':
        messages.error(request, "This room is not available for booking.")
        return redirect('hotel:room_detail', pk=room_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                client = request.user.client
                check_in_date = form.cleaned_data['check_in_date']
                check_out_date = form.cleaned_data['check_out_date']
                special_requests = form.cleaned_data['special_requests']
                
                # Calculate total price
                days = (check_out_date - check_in_date).days
                total_price = room.category.base_price * days
                
                # Create reservation
                reservation = Reservation.objects.create(
                    client=client,
                    room=room,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    status='confirmed',
                    total_price=total_price,
                    special_requests=special_requests
                )
                
                # Update room status
                room.status = 'reserved'
                room.save()
                
                messages.success(request, f"Room {room.room_number} booked successfully!")
                return redirect('hotel:client_dashboard')
                
            except Exception as e:
                messages.error(request, f"Error booking room: {str(e)}")
    else:
        # Default check-in to today and check-out to tomorrow
        form = BookingForm(initial={
            'check_in_date': date.today(),
            'check_out_date': date.today() + timedelta(days=1)
        })
    
    return render(request, 'hotel/client/book_room.html', {
        'form': form,
        'room': room
    })