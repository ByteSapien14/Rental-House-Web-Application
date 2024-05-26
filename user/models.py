from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth import get_user_model

# # Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, email, name, location, city, state, number, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have a password')
        if not name:
            raise ValueError('User must have a full name')

        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.set_password(password)
        user.location = location
        user.city = city
        user.state = state
        user.number = number
        user.admin = is_admin
        user.staff = is_staff
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, email, state, city, location,name, number, password=None):
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have a password')
        if not name:
            raise ValueError('User must have a full name')

        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.number = number
        user.city = city
        user.state = state
        user.location = location
        user.set_password(password)
        user.admin = True
        user.staff = True
        user.active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):

    email = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=25)
    password = models.CharField(max_length=100)
    location = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    number = models.IntegerField(default=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True)  # Add this line
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','location', 'city', 'state', 'number']
    objects = UserManager()

    def __str__(self):
        return self.email

    @staticmethod
    def has_perm(perm, obj=None):
        return True

    @staticmethod
    def has_module_perms(app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def user_active(self):
        return self.active


class House(models.Model):
    house_id = models.AutoField(primary_key=True)
    user_email = models.ForeignKey(
        'user.User', on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    cost = models.IntegerField()
    bedroom = models.IntegerField()
    kitchen = models.CharField(max_length=20)
    desc = models.CharField(max_length=200)
    date = models.DateField(auto_now=True, auto_now_add=False)
    available = models.BooleanField(default=True)
    PAYMENT_OPTIONS = [
        ('flat_fee', 'House Fee Per Advert (20,000)'),
        ('subscription', 'Subscription Plan (100,000 Yearly)'),
    ]
    PAYMENT_METHODS = [
        ('mobile_money', 'Mobile Money'),
        ('credit_card', 'Credit Card'),
    ]
    payment_option = models.CharField(max_length=100, choices=PAYMENT_OPTIONS)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHODS)

    def toggle_availability(self):
        self.available = not self.available
        self.save()

    def __str__(self):
        return str(self.house_id)


class HouseImage(models.Model):
    house = models.ForeignKey(
        House, related_name='img', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='house_images/')


class Contact(models.Model):
    contact_id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=100, default=True) 
    email = models.EmailField(max_length=100)
    body = models.CharField(max_length=500)

    def __str__(self):
        return str(self.contact_id)


class Tenant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    phone_number = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_number = models.CharField(max_length=15)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE)


class Income(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date = models.DateField()
    tenant = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)


class Expense(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE)
