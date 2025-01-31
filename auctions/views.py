from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Listing, Comment, Bid, Watchlist, Category
from .models import User
from .forms import CommentForm, ListingCreateForm
from django.contrib import messages


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html",{
        'listings': listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


## my code 

def details(request, title):
    listing= get_object_or_404(Listing, title=title)
    latest_bid = listing.bids.latest('amount').amount if listing.bids.exists() else listing.starting_bid
    bids = listing.bids.all()
    is_winner = request.user.is_authenticated and not listing.is_active and listing.winner == request.user

    comments = listing.comment.all()
    comment_form = CommentForm()
    if request.method == "POST" and request.user.is_authenticated:
        is_in_watchlist=Watchlist.objects.filter(user=request.user, listings = listing).exists() 
        print(is_in_watchlist)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.listing = listing
            comment.user = request.user
            comment.save()
            
            return render(request, 'auctions/details.html',{
                'listing':listing,
                'bids':bids,
                'latest':latest_bid,
                'comments':comments,
                'comment_form': comment_form,
                "is_winner": is_winner,
                'is_in_watchlist':is_in_watchlist
            })
    else:
           form =CommentForm()
           if request.user.is_authenticated:
              is_in_watchlist=Watchlist.objects.filter(user=request.user, listings = listing).exists()
              return render(request, 'auctions/details.html',{
               'listing':listing,
                'bids':bids,
                'latest':latest_bid,
                'comments':comments,
                'comment_form': comment_form,
                "is_winner": is_winner,
                "is_in_watchlist":is_in_watchlist
                })
           else:
              is_in_watchlist = False
              return render(request, 'auctions/details.html',{
               'listing':listing,
                'bids':bids,
                'latest':latest_bid,
                'comments':comments,
                'comment_form': comment_form,
                "is_winner": is_winner,
                "is_in_watchlist":is_in_watchlist
                })
               

    is_in_watchlist=Watchlist.objects.filter(user=request.user, listings = listing).exists()
    return render(request, 'auctions/details.html',{
       'listing':listing,
        'bids':bids,
        'latest':latest_bid,
        'comments':comments,
        'comment_form': comment_form,
        "is_winner": is_winner,
        "is_in_watchlist":is_in_watchlist
        
    })

#def bid_on_listing(request, title):
   # listing = get_object_or_404(Listing, title=title)
   # if request.method == 'POST':
   #     bid_amount = request.POST.get('amount')
   #     if float(bid_amount)>=listing.starting_bid and (not listing.bids.exists() or float(bid_amount)> listing.bids.latest('amount').amount):
   ##         Bid.objects.create(listing=listing, user=request.user, amount= bid_amount)
    #        print("it workss well")
    #        return redirect('details', title=title)
    #    else:
    #        pass
    
   # return redirect('details', title=title)

def bid_on_listing(request, title):
    item = get_object_or_404(Listing, title=title)
    current_highest_bid = Bid.objects.filter(listing=item).order_by('-amount').first()

    if request.method == 'POST':
        bid_amount = request.POST.get('amount')

        try:
            bid_amount = float(bid_amount)
        except ValueError:
            messages.error(request, "Invalid bid amount. Please enter a number.")
            return render(request, 'auctions/details.html', {'item': item})

        
        if bid_amount < item.starting_bid:
            messages.error(request, f"Your bid must be at least {item.starting_bid}.")
            return redirect('details', title = title)
        elif current_highest_bid and bid_amount <= current_highest_bid.amount:
            messages.error(request, f"Your bid must be greater than the current highest bid of {current_highest_bid.amount}.")
            return redirect('details', title = title)
        else:
            
            Bid.objects.create(listing=item, user=request.user, amount=bid_amount)
            messages.success(request, "Your bid has been placed successfully!")
            return redirect('details', title = title)

    return render(request, 'auctions/details.html', {'listing': item})


def create(request):
    if request.method == 'POST':
        form = ListingCreateForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            return redirect('index')
    form = ListingCreateForm()
    return render(request, 'auctions/create.html',{
        'form': form
    })

def add_to_watchlist(request, title):
    if request.method == "POST":
        
        listing = get_object_or_404(Listing, title=title)
        is_in_watchlist = Watchlist.objects.filter(user=request.user, listings=listing).exists() 
        
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)

        if listing in watchlist.listings.all():
            watchlist.listings.remove(listing)
            listings = watchlist.listings.all()
            
            return render(request, 'auctions/watchlist.html',{
            'is_in': is_in_watchlist,
            'watchlist': watchlist,
            'listings':listings
        })
        else:
            watchlist.listings.add(listing)
            listings = watchlist.listings.all()
            
            return render(request, 'auctions/watchlist.html',{
            'is_in': is_in_watchlist,
            'watchlist': watchlist,
            'listings':listings
        })
    print("idrice")    
    return render(request, 'auctions/watchlist.html',{
        "name" :"Empty list"
    })

def watchlist_view(request):
    watchlist = Watchlist.objects.filter(user=request.user, listings__isnull=False).first()
    if watchlist:
        
        listings = watchlist.listings.all()
        return render(request, 'auctions/watchlist.html', 
                      {'listings': listings,
                       'watchlist': watchlist
                       })
    else:
        
        return render(request, 'auctions/watchlist.html',{
            "element":"your list is empty"
        })

  #  watchlist = get_object_or_404(Watchlist, user=request.user)
   # watchlist = Watchlist.objects.get(user=request.user)
    #if watchlist:
    # is_in_watchlist = Watchlist.objects.filter(user=request.user, listings=watchlist.objects.get).exists() 
    #    return render(request, 'auctions/watchlist.html',{
     #       'watchlist':watchlist,
        #   'is_in': is_in_watchlist
    #    })
   # return render(request,'auctions/watchlist.html',{
    #    "element":"your list is empty"
   # })

##close bid
def close(request, title):
    listing = get_object_or_404(Listing, title=title)

    if request.user.is_authenticated and request.user == listing.created_by:
        highest_bid = listing.bids.order_by('-amount').first()
        if highest_bid:
            listing.winner = highest_bid.user
        listing.is_active = False
        listing.save()
        return redirect('details', title=title)  
    
    

def category(request):
    cat = Category.objects.all()
    return render(request, 'auctions/category.html',{
        'category':cat
    })

def listing_in_categorie(request, title):
    category = get_object_or_404(Category, name=title)
    listings = category.listings.filter(is_active=True)
    return render(request, 'auctions/categorylisting.html',{
        'category':category,
        'listings': listings
    })