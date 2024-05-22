import email
from django.shortcuts import render
from .models import User


def profile(request):
	
	user = User.objects.filter(email= email)
	context = {
		'user':user,
	}
	return render(request, 'user/profile.html')

