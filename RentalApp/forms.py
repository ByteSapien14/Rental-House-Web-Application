from django.utils.html import escape
from django.utils.dateparse import parse_date
from django import forms
from user.models import House, HouseImage, User, Tenant, Contact, Income, Expense
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils import timezone


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@gmail.com'):
            raise ValidationError(
                "Only email addresses like @gmail.com domain are allowed.")
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        cleaned_password = password.strip()
        return cleaned_password

    def authenticate_user(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        user = authenticate(email=email, password=password)

        if not user:
            raise ValidationError("Invalid email or password.")

        return user


class HousePostForm(forms.ModelForm):
    payment_option = forms.ChoiceField(choices=(
        ('flat_fee', 'House Fee Per Advert (20,000)'),
        ('subscription', 'Subscription Plan (100,000 Yearly)'),
    ))
    payment_method = forms.ChoiceField(choices=(
        ('mobile_money', 'Mobile Money'),
        ('credit_card', 'Credit Card'),
    ))

    class Meta:
        model = House
        fields = ['location', 'city', 'state', 'cost', 'kitchen',
                  'bedroom', 'desc', 'payment_option', 'payment_method']

    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data.get('cost')
        if cost is not None and cost <= 0:
            raise ValidationError("Cost must be greater than 0.")

        return cleaned_data


class ImageForm(forms.ModelForm):
    class Meta:
        model = HouseImage
        fields = ['img']


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    email = forms.EmailField()
    body = forms.CharField(widget=forms.Textarea)

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        return subject

    def clean_body(self):
        body = self.cleaned_data['body']
        # Clean and escape HTML tags to prevent XSS attacks
        cleaned_body = escape(body)
        return cleaned_body

    def save(self):
        subject = self.cleaned_data['subject']
        email = self.cleaned_data['email']
        body = self.cleaned_data['body']

        # Save the contact message to the database using your model
        message = Contact.objects.create(
            subject=subject,
            email=email,
            body=body
        )
        return message


class SignUpForm(forms.Form):
    email = forms.EmailField(
        max_length=100, help_text='Required. Inform of a valid email address.')
    name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    number = forms.IntegerField()
    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=(
            "Your password must contain at least 8 characters."),
    )
    password2 = forms.CharField(
        label=("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=("Enter the same password as before, for verification."),
    )
    profile_picture = forms.ImageField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = User.objects.create(
            email=self.cleaned_data['email'],
            name=self.cleaned_data['name'],
            location=self.cleaned_data['location'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            number=self.cleaned_data['number'],
            profile_picture=self.cleaned_data['profile_picture']
        )
        # Hash password
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class TenantRegistrationForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'email', 'lease_start_date', 'lease_end_date',
                  'phone_number', 'emergency_contact_name', 'emergency_contact_number']
        widgets = {
            'lease_start_date': forms.DateInput(attrs={'type': 'date'}),
            'lease_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        lease_start_date = cleaned_data.get("lease_start_date")
        lease_end_date = cleaned_data.get("lease_end_date")

        if lease_start_date and lease_end_date:
            lease_start_date_str = str(lease_start_date)
            lease_end_date_str = str(lease_end_date)

            if parse_date(lease_end_date_str) < parse_date(lease_start_date_str):
                raise ValidationError(
                    "The lease end date cannot be before the lease start date.")
        return cleaned_data


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date', 'tenant', 'amount', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        status = cleaned_data.get('status')

        # Perform additional validation here if needed
        if status == 'paid' and date > timezone.now().date():
            raise forms.ValidationError("Paid date cannot be in the future.")

        return cleaned_data


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'description', 'amount', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount can't be below 0")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        description = cleaned_data.get('description')
        status = cleaned_data.get('status')

        if description == '':
            raise ValidationError("Description can't be empty")
        if date == '':
            raise ValidationError("Date can't be empty")
        if status == 'paid' and date > timezone.now().date():
            raise forms.ValidationError("Paid date cannot be in the future.")
        
        return cleaned_data
