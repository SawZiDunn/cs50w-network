from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json 
from .models import User, Follow, Like, Post


def index(request): 
    posts = Post.objects.all().order_by('-created')

    paginator = Paginator(posts, 10)
    page_no = request.GET.get('page')
    page_posts = paginator.get_page(page_no)

    likes = Like.objects.all()
    myLikePostObjects = []
    for like in likes:
        if like.user == request.user:
            myLikePostObjects.append(like.post)

    return render(request, "network/index.html", {
        "page_posts": page_posts,
        "myLikePostObjects": myLikePostObjects,
    })

def new_post(request):
    if request.method == "POST":
        description = request.POST["description"]

        new_post = Post(description=description, owner=request.user)
        new_post.save()

        return HttpResponseRedirect(reverse(index))

def following(request):

    followings = Follow.objects.filter(follower=request.user)
    posts = []
    for following in followings:
        posts += following.user.posts.all().order_by('-created')

    paginator = Paginator(posts, 10)
    page_no = request.GET.get('page')
    page_posts = paginator.get_page(page_no)

    return render(request, "network/following.html", {
        "page_posts": page_posts,
    })


def profile(request, user_id):
    user = User.objects.get(id=user_id)
    posts = Post.objects.filter(owner=user).order_by('-created')

    paginator = Paginator(posts, 10)
    page_no = request.GET.get('page')
    page_posts = paginator.get_page(page_no)

    # for Follow and Unfollow
    if request.method == "POST":
        if request.POST['following'] == 'follow':
            to_create = Follow(user=user, follower=request.user)
            if not Follow.objects.filter(user=user, follower=request.user).exists():
                to_create.save()
        else:
            to_delete = Follow.objects.get(user=user, follower=request.user)
            to_delete.delete()

    followers = user.followers.all()
    # followers = Follow.objects.filter(user=user)

    followings = user.followings.all()
    # followings = Follow.objects.filter(follower=user)

    is_following = False
    if Follow.objects.filter(user=user, follower=request.user).exists():
        is_following = True
        

    return render(request, "network/profile.html", {
        "page_posts": page_posts,
        "followers": len(followers),
        "followings": len(followings),
        "is_following": is_following,
        "post_owner": user,
    })

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        post.description = data["description"]
        post.save()
        
        return JsonResponse({"message": "Changes Successful!", "data": data["description"]})
    
def like(request, post_id):
    if request.method == "PUT":
        # data = json.loads(request.body)
        post = Post.objects.get(id=post_id)

        if not Like.objects.filter(user=request.user, post=post).exists():
            Like.objects.create(user=request.user, post=post)
            return JsonResponse({"isLike": "Unlike", "likeCount": len(post.post_likes.all())})
        else:
            like_obj = Like.objects.get(user=request.user, post=post)
            like_obj.delete()
            return JsonResponse({"isLike": "Like", "likeCount": len(post.post_likes.all())})
        
        

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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
