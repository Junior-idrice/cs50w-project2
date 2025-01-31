from django.urls import path

from . import views
from commerce import settings
from django.conf.urls.static import static
urlpatterns = [
    path('catL/<str:title>/', views.listing_in_categorie, name='catL'),
    path('categories', views.category, name='category'),
    path('addwatch/<str:title>/', views.add_to_watchlist, name='addto'),
    path("create", views.create, name='create'),
    path("details/<str:title>", views.details, name="details"),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('bid/<str:title>/', views.bid_on_listing, name='bid_on_listing'),
    path('watchlist', views.watchlist_view, name='watchlist'),
    path('close/<str:title>', views.close, name="close"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
