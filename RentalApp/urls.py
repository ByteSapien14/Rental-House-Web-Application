from django.urls import include, path
from django.contrib import admin
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView


admin.site.site_header = "Rental Admin"
admin.site.site_title = "Rental Admin Portal"
admin.site.index_title = "Welcome to Rental Admin Portal"

admin.autodiscover()
urlpatterns = [
    path('', RedirectView.as_view(url='/index/')),

    path('index/', views.index, name='index'),

    path('home/', views.home, name='home'),

    path('contact/', views.contact, name='contact'),

    path('about/', views.about, name='about'),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),

    path('register/', views.register, name='register'),

    path('register-tenant/', views.register_tenant, name='register_tenant'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile, name='profile'),

    path('posth/', views.posth, name='posth'),

    path('descr/', views.descr, name='descr'),

    path('tenant/', views.tenant, name='tenant'),

    path('deleteh/', views.deleteh, name='deleteh'),

    path('toggle-availability/<int:house_id>/',
         views.toggle_availability, name='toggle_availability'),

    path('search/', views.search, name='search'),

    path('financial-management/', views.financial_management,
         name='financial_management'),

    path('register-income/', views.register_income, name='register_income'),

    path('register-expense/', views.register_expense, name='register_expense'),
]

urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
