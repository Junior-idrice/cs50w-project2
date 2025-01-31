from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass
class Category(models.Model):
    name = models.CharField(max_length=180)

    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.ImageField(upload_to='products', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='idrice')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="listings")
    is_active = models.BooleanField(default=True)
    winner  = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="won_listing")

    def __str__(self):
        return self.title
    
class Bid(models.Model):
    listing = models.ForeignKey(Listing, related_name='bids',on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, related_name='comment', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} : {self.text}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Listing, blank=True)

    def __str__(self):
        return f"{self.user.username}'s watchlist"