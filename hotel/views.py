from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import inlineformset_factory
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django import forms
from datetime import date, timedelta, datetime
from django.db.models import Min, Max, Count, Sum
from collections import Counter
from statistics import median, mode
from django.db.models.functions import TruncMonth
import requests
from .models import (
    Article, CompanyInfo, FAQ, Staff, Vacancy, Review, 
    PromoCode, Room, RoomCategory, RoomImage, Reservation, Client, Service,
    Banner, Partner, Cart, CartItem, Order, OrderItem
)
from .forms import RoomForm, RoomImageForm, RoomFilterForm, ReviewForm
from .auth_forms import UserRegisterForm, UserLoginForm, UserProfileForm
import matplotlib.pyplot as plt
from io import BytesIO
from django.core.files.base import ContentFile
from .models import ChartImage
from django.db.models import Q

def home(request):
    latest_article = Article.objects.filter(is_published=True).order_by('-published_date').first()
    daily_quote = get_daily_quote()
    exchange_rates = get_exchange_rates()
    banners = Banner.objects.filter(is_active=True).order_by('order')
    partners = Partner.objects.all()
    featured_services = Service.objects.filter(is_available=True)[:6]  # Show first 6 services
    
    context = {
        'latest_article': latest_article,
        'daily_quote': daily_quote,  
        'exchange_rates': exchange_rates,
        'banners': banners,
        'partners': partners,
        'featured_services': featured_services,
    }
    
    return render(request, 'hotel/home.html', context)

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

def services(request):
    """View for displaying available hotel services"""
    available_services = Service.objects.filter(is_available=True)
    return render(request, 'hotel/services.html', {
        'services': available_services
    })

class RoomListView(ListView):
    model = Room
    template_name = 'hotel/room_list.html'
    context_object_name = 'rooms'
    
    def get_queryset(self):
        queryset = Room.objects.all()
        form = RoomFilterForm(self.request.GET)
        
        if form.is_valid():
            if form.cleaned_data.get('category'):
                queryset = queryset.filter(category=form.cleaned_data['category'])
            
            if form.cleaned_data.get('min_price'):
                queryset = queryset.filter(category__base_price__gte=form.cleaned_data['min_price'])
            
            if form.cleaned_data.get('max_price'):
                queryset = queryset.filter(category__base_price__lte=form.cleaned_data['max_price'])
            
            if form.cleaned_data.get('capacity'):
                queryset = queryset.filter(capacity__gte=form.cleaned_data['capacity'])
            
            if form.cleaned_data.get('available_only'):
                queryset = queryset.filter(status='available')
            
            search_query = form.cleaned_data.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(room_number__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(category__name__icontains=search_query)
                )
            
            sort_by = form.cleaned_data.get('sort_by')
            if sort_by:
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('room_number')
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = RoomCategory.objects.all()
        context['is_staff'] = self.request.user.is_staff or self.request.user.is_superuser
        context['filter_form'] = RoomFilterForm(self.request.GET)
        context['min_room_price'] = RoomCategory.objects.aggregate(Min('base_price'))['base_price__min'] or 0
        context['max_room_price'] = RoomCategory.objects.aggregate(Max('base_price'))['base_price__max'] or 1000
        return context

class RoomDetailView(DetailView):
    model = Room
    template_name = 'hotel/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.request.user.is_staff or self.request.user.is_superuser
        return context

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
            
            image_formset.instance = self.object
            image_formset.save()
            
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def test_func(self):
        return is_staff_user(self.request.user)

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
            
            image_formset.instance = self.object
            image_formset.save()
            
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def test_func(self):
        return is_staff_user(self.request.user)

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

RoomImageFormSet = inlineformset_factory(
    Room, 
    RoomImage, 
    form=RoomImageForm, 
    extra=1, 
    can_delete=True
)

def is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

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
    has_children = forms.BooleanField(
        required=False, 
        label="Бронирование с детьми?",
        help_text="Отметьте, если с вами будут дети"
    )
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
                has_children = form.cleaned_data['has_children']
                
                days = (check_out_date - check_in_date).days
                total_price = room.category.base_price * days
                
                reservation = Reservation.objects.create(
                    client=client,
                    room=room,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    status='confirmed',
                    total_price=total_price,
                    special_requests=special_requests,
                    has_children=has_children 
                )
                
                
                room.status = 'reserved'
                room.save()
                
                messages.success(request, f"Room {room.room_number} booked successfully!")
                return redirect('hotel:client_dashboard')
                
            except Exception as e:
                messages.error(request, f"Error booking room: {str(e)}")
    else:
        form = BookingForm(initial={
            'check_in_date': date.today(),
            'check_out_date': date.today() + timedelta(days=1)
        })
    
    return render(request, 'hotel/client/book_room.html', {
        'form': form,
        'room': room
    })

def get_daily_quote():
    """Get a daily quote from FavQs API"""
    url = "https://favqs.com/api/qotd"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            quote_data = {
                'quote': data['quote']['body'],
                'author': data['quote']['author']
            }
            return quote_data
        else:
            print(f"FavQs API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching daily quote: {e}")
        return None

def get_exchange_rates(base_currency="USD"):
    """Get current exchange rates"""
    api_key = "0da4b4143b44e87f2cf45a11"  
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        
        if response.status_code == 200 and data['result'] == 'success':
            rates = {
                'EUR': data['conversion_rates'].get('EUR'),
                'GBP': data['conversion_rates'].get('GBP'),
                'BYN': data['conversion_rates'].get('BYN'),
                'RUB': data['conversion_rates'].get('RUB'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return rates
        else:
            return None
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return None

@login_required
@user_passes_test(is_staff_user)
def statistics_view(request):
    """View for displaying hotel statistics and analytics"""
    
    rooms_by_category = Room.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('category__name')
    
    total_revenue = Reservation.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    reservation_amounts = list(Reservation.objects.values_list('total_price', flat=True))
    if reservation_amounts:
        avg_sale = sum(reservation_amounts) / len(reservation_amounts)
        median_sale = median(reservation_amounts)
        try:
            mode_sale = mode(reservation_amounts)
        except:
            counter = Counter(reservation_amounts)
            mode_sale = counter.most_common(1)[0][0]
    else:
        avg_sale = median_sale = mode_sale = 0
    
    popular_categories = RoomCategory.objects.annotate(
        reservation_count=Count('rooms__reservations')
    ).order_by('-reservation_count')
    
    profitable_categories = RoomCategory.objects.annotate(
        revenue=Sum('rooms__reservations__total_price')
    ).order_by('-revenue')
    
    monthly_revenue = Reservation.objects.annotate(
        month=TruncMonth('check_in_date')
    ).values('month').annotate(
        revenue=Sum('total_price')
    ).order_by('month')
    
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status__in=['occupied', 'reserved']).count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    reservations = Reservation.objects.all()
    if reservations:
        stay_durations = []
        for reservation in reservations:
            duration = (reservation.check_out_date - reservation.check_in_date).days
            stay_durations.append(duration)
        avg_stay = sum(stay_durations) / len(stay_durations)
        median_stay = median(stay_durations)
    else:
        avg_stay = median_stay = 0
    
    context = {
        'rooms_by_category': rooms_by_category,
        'total_revenue': total_revenue,
        'avg_sale': avg_sale,
        'median_sale': median_sale,
        'mode_sale': mode_sale,
        'popular_categories': popular_categories,
        'profitable_categories': profitable_categories,
        'monthly_revenue': monthly_revenue,
        'occupancy_rate': occupancy_rate,
        'avg_stay': avg_stay,
        'median_stay': median_stay,
    }
    
    return render(request, 'hotel/statistics.html', context)

@login_required
@user_passes_test(is_staff_user)
def room_booking_distribution_chart(request):
    """Generate a bar chart for room bookings by category and save to media directory."""
    categories = RoomCategory.objects.annotate(
        booking_count=Count('rooms__reservations')
    ).order_by('-booking_count')

    category_names = [category.name for category in categories]
    booking_counts = [category.booking_count for category in categories]

    plt.figure(figsize=(10, 6))
    plt.bar(category_names, booking_counts, color='skyblue')
    plt.title('Room Bookings by Category')
    plt.xlabel('Room Category')
    plt.ylabel('Number of Bookings')
    plt.xticks(rotation=45, ha='right')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()      

    filename = f'room_bookings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    chart_image = ChartImage(title='Room Booking Distribution')
    
    chart_image.image.save(filename, ContentFile(buffer.getvalue()), save=True)
    
    return render(request, 'hotel/visualizations/room_booking_distribution.html', {
        'chart_image': chart_image
    })

def add_review(request):
    """Allow registered users to submit reviews"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            try:
                client = request.user.client
                review.client = client
                review.is_published = False 
                review.save()
                messages.success(request, "Thanks for the feedback")
                return redirect('hotel:reviews')
            except:
                messages.error(request, "Your account is not set up as a client. Please contact support.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ReviewForm()
    
    published_reviews = Review.objects.filter(is_published=True).order_by('-date_posted')
    
    return render(request, 'hotel/reviews.html', {
        'form': form,
        'reviews': published_reviews
    })

def service_detail(request, pk):
    """Detail view for a specific service"""
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'hotel/service_detail.html', {'service': service})

def get_or_create_cart(request):
    """Helper function to get or create a cart"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, service_id):
    """Add a service to the shopping cart"""
    service = get_object_or_404(Service, id=service_id)
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        service=service,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, f"'{service.name}' добавлен в корзину.")
    return redirect('hotel:cart_view')

def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    service_name = cart_item.service.name
    cart_item.delete()
    messages.info(request, f"'{service_name}' удален из корзины.")
    return redirect('hotel:cart_view')

def update_cart(request, item_id):
    """Update quantity of an item in the cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Количество обновлено.")
        else:
            service_name = cart_item.service.name
            cart_item.delete()
            messages.info(request, f"'{service_name}' удален из корзины.")
    
    return redirect('hotel:cart_view')

def cart_view(request):
    """Display the shopping cart"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.total_price,
        'items_count': cart.items_count,
    }
    
    return render(request, 'hotel/cart.html', context)

def checkout_view(request):
    """Checkout process"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('hotel:home')
    
    context = {
        'cart': cart,
        'total_price': cart.total_price,
    }
    
    return render(request, 'hotel/checkout.html', context)

def payment_view(request):
    """Payment processing"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('hotel:home')
    
    if request.method == 'POST':
        # Process payment (this is a simplified version)
        email = request.POST.get('email')
        if not email and request.user.is_authenticated:
            email = request.user.email
            
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            total_amount=cart.total_price,
            status='paid'  # In real app, this would be set after payment confirmation
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                service=cart_item.service,
                quantity=cart_item.quantity,
                price=cart_item.service.price
            )
        
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, f"Заказ #{order.id} успешно оплачен! Спасибо за покупку.")
        return redirect('hotel:order_success', order_id=order.id)
    
    context = {
        'cart': cart,
        'total_price': cart.total_price,
    }
    
    return render(request, 'hotel/payment.html', context)

def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'hotel/order_success.html', {'order': order})