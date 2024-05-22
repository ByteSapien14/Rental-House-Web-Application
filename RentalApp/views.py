from .forms import TenantRegistrationForm
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from user.models import *
from django.contrib import messages
from RentalApp.forms import HousePostForm, LoginForm, ImageForm, SignUpForm, ContactForm, IncomeForm, ExpenseForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.mail import send_mail

def index(request):
    houses = House.objects.prefetch_related('img')  
    context = {'house_list': houses}
    return render(request, 'index.html', context)


def home(request):
    context = {
        'msg': 'Search your query'
    }
    return render(request, 'home.html', context)


def tenant(request):
    tenants = Tenant.objects.all()  # Query for all tenants
    context = {'tenants': tenants}  # Add tenants to the context
    return render(request, 'financial_management.html', context)


def search(request):
    if request.method == 'GET':
        typ = request.GET.get('type')
        q = request.GET.get('q')
        availability = request.GET.get('availability')
        bedroom_number = request.GET.get('bedroom_number')

        context = {'type': typ, 'q': q, 'availability': availability,
                   'bedroom_number': bedroom_number}

        results = []

        if typ == 'House':
            houses = House.objects.filter(Q(location=q) | Q(city=q))
            if availability:
                if availability == 'available':
                    houses = houses.filter(available=True)
                elif availability == 'unavailable':
                    houses = houses.filter(available=False)
            if bedroom_number:
                houses = houses.filter(bedroom=bedroom_number)

            if houses.exists():
                for house in houses:
                    house_images = HouseImage.objects.filter(house=house)
                    results.append((house, house_images))
            else:
                context['error_message'] = "No matching results for your query.."

        context['result'] = results

        return render(request, 'home.html', context)
    
def about(request):
    context = {}

    context['house'] = House.objects.all()

    return render(request, 'about.html', context)


def logout_view(request):
    # End the session
    request.session.flush()
    # Pass a flag to indicate logout
    return render(request, 'index.html', {'logged_out': True})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message to the database
            instance = form.save()

            # Get cleaned data from the form
            email_receiver = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']

            try:
                # Send email notification
                send_mail(
                    subject,
                    body,
                    settings.EMAIL_HOST_USER,
                    [email_receiver],
                    fail_silently=False,
                )
                messages.success(request, 'Message sent successfully')
                return redirect('contact')  # Redirect to avoid resubmission
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
        else:
            messages.error(
                request, 'Invalid form data. Please correct the errors.')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def descr(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        context = {}

        house = House.objects.get(house_id=id)
        house_images = HouseImage.objects.filter(house=house)

        context['val'] = house
        context['type'] = 'House'
        context['user'] = User.objects.get(email=house.user_email)
        context['images'] = house_images  # Pass the images to the context
        # Add availability status to context
        context['is_available'] = house.available

        return render(request, 'desc.html', context)


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the user object without profile_picture
            user = get_user_model().objects.create_user(
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                location=form.cleaned_data['location'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                number=form.cleaned_data['number'],
                password=form.cleaned_data['password1']
            )
            # Now update the user object with profile_picture if provided
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                try:
                    # Set profile_picture and save user object
                    user.profile_picture = profile_picture
                    user.save()
                except ValidationError as e:
                    # Handle validation error for profile_picture
                    form.add_error('profile_picture', e)
                    return render(request, 'register.html', {'form': form})
            # Redirect to a success page or do whatever you need
            return redirect('/profile/')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


@login_required(login_url='/login/')
def profile(request):
    report = Contact.objects.filter(email=request.user.email)
    houses = House.objects.filter(user_email=request.user)
    house_with_images = []

    for house in houses:
        house_images = HouseImage.objects.filter(house=house)
        house_with_images.append((house, house_images))

    context = {
        'user': request.user,
        'report': report,
        'reportno': report.count(),
        'houseno': houses.count(),
        'house_with_images': house_with_images,
        'houses': houses
    }

    return render(request, 'profile.html', context=context)


@login_required(login_url='/login/')
def posth(request):
    if request.method == "POST":
        form = HousePostForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            try:
                house = form.save(commit=False)
                house.user_email = request.user
                house.save()

                # Save images related to the house
                # Change 'images' to 'img'
                for img in request.FILES.getlist('img'):
                    HouseImage.objects.create(house=house, img=img)

                messages.success(request, 'Submitted successfully')
                return redirect('posth')
            except Exception as e:
                messages.error(request, f'Error submitting data: {e}')
        else:
            messages.error(
                request, 'Form data is invalid. Please check the input fields.')
    else:
        form = HousePostForm()
        image_form = ImageForm()
    houses = House.objects.all()
    return render(request, 'posth.html', {'form': form, 'image_form': image_form, 'houses': houses})


def deleteh(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        instance = House.objects.get(house_id=id)
        instance.delete()
        messages.success(request, 'House details deleted successfully')
        return redirect('/profile/')


def toggle_availability(request, house_id):
    # Retrieve the house object
    house = get_object_or_404(House, house_id=house_id)

    # Toggle the availability
    house.available = not house.available
    house.save()

    # Return a JSON response indicating success and the new availability status
    return JsonResponse({'success': True, 'available': house.available})


def login_view(request):
    if request.method == 'GET':
        form = LoginForm()  # Initialize the LoginForm
        return render(request, 'login.html', {'form': form})

    elif request.method == 'POST':
        form = LoginForm(request.POST)  # Bind the form with POST data

        # Retrieve the current login attempt count from the session
        login_attempts = request.session.get('login_attempts', 0)

        if login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            messages.error(
                request, 'Maximum login attempts exceeded. Please try again later.')
            # Redirect to the same page using GET
            return HttpResponseRedirect(request.path)

        if form.is_valid():  # Check if the form data is valid
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if the provided email exists in the database
            if User.objects.filter(email=email).exists():
                user = authenticate(request, email=email, password=password)

                if user is not None:
                    login(request, user)
                    # Reset login attempt count upon successful login
                    request.session['login_attempts'] = 0
                    return redirect("/")
                else:
                    messages.error(request, 'Email and password do not match')
            else:
                messages.error(request, 'Email does not exist')

        # Increment login attempt count if authentication fails
        request.session['login_attempts'] = login_attempts + 1

        # If form is invalid or authentication fails, render the login page with the form and error message
        return render(request, 'login.html', {'form': form})


@login_required(login_url='/login/')
def register_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user_id = request.user.email
            income.save()
            messages.success(request, 'Income registered successfully!')
            return redirect('profile')
    else:
        form = IncomeForm()
    return render(request, 'register_income.html', {'form': form})


@login_required(login_url='/login/')
def register_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user_id = request.user.email
            expense.save()
            messages.success(request, 'Expense registered successfully!')
            return redirect('profile')
    else:
        form = ExpenseForm()
    return render(request, 'register_expense.html', {'form': form})


@login_required(login_url='/login/')
def register_tenant(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST)
        if form.is_valid():
            tenant = form.save(commit=False)
            tenant.user_id = request.user.email  # Use the email as the user's primary key
            tenant.save()
            # Add success message
            messages.success(request, 'Tenant registered successfully!')
            # Redirect to the tenant management page after registration
            return redirect('profile')
    else:
        form = TenantRegistrationForm()
    return render(request, 'register_tenant.html', {'form': form})


@login_required(login_url='/login/')
def financial_management(request):
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    tenants = Tenant.objects.filter(user=request.user)
    income_form = IncomeForm()
    expense_form = ExpenseForm()
    context = {
        'incomes': incomes,
        'expenses': expenses,
        'tenants': tenants,
        'income_form': income_form,
        'expense_form': expense_form,
    }
    return render(request, 'financial_management.html', context)
