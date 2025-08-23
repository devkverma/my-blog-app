from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count

# Create your views here.

def home (request):
    try:
        if request.user.is_authenticated:
            return JsonResponse(
                {
                    "status" : 200,
                    "redirect_to" : reverse("dashboard"),
                },
                status = 200
            )
        
        data = {
            'status': 200,
            'urls': {
                # 'login': redirect('login'),
                # 'signup': redirect('signup'),
                # 'leaderboard': redirect('leaderboard'),
                # 'posts': redirect('posts'),
            },
            'content': {
                'Heading': 'Welcome',
                'Body': 'lorem ipsum'
            }
        }
        return JsonResponse(data, status=200)
    except Exception:
        return JsonResponse({'status': 500, 'content': 'Internal Server Error'}, status=500)
    
def not_authorized(request):
    if request.user.is_authenticated:
        return JsonResponse(
            {
                'status' : 403,
                'message' : 'User not authorized',
                'redirect_to' : reverse('dashboard')
            },
            status=403
        )
    
    return JsonResponse(
        {
            'status' : 403,
            'message' : 'User not authorized',
            'redirect_to' : reverse('home')
        },
        status = 403
    )

def page_not_found (request, exception):
    return JsonResponse(
        {
            'status' : 404,
            'message' : "Oops! Page doesn't exist"
        },
        status = 404
    )

@csrf_exempt    #@csrf_protect
def user_signup (request):
    if request.user.is_authenticated:
        return JsonResponse(
            {
                'status' : 200,
                'message' : 'User already exists and logged in',
                'redirect_to' : reverse('dashboard'),
            },
            status = 200
        )
    
    if request.method == 'POST':
        username = (request.POST.get('username')).strip()
        email = (request.POST.get('email')).strip()
        password = (request.POST.get('password')).strip()
        first_name = (request.POST.get('first_name')).strip().capitalize()
        last_name = (request.POST.get('last_name')).strip().capitalize()


        if CustomUser.objects.filter(username = username).exists():
            return JsonResponse(
                {
                    'status' : 409,
                    'message' : 'Username is taken',
                },
                status = 409
            )
        
        if len(password) < 8:
            return JsonResponse(
                {
                    'status' : 400,
                    'message' : "Bad request: Passwords can't be less than 8 characters"
                },
                status = 400
            )
        
        user = CustomUser.objects.create_user(
            username = username,
            email = email,
            password = password,
            first_name = first_name,
            last_name = last_name
        )

        BlogUser.objects.create(user = user)

        return JsonResponse(
            {
                'status' : 200,
                'message' : 'Registration complete',
                'redirect_to' : reverse('login')
            },
            status = 200
        )
    
    return JsonResponse(
        {
            'status' : 200,
            'message' : 'Create a new user',
            'redirect_to' : reverse('signup'),
        },
        status = 400
    )

@csrf_exempt
def user_login (request):
    if request.user.is_authenticated:
        return JsonResponse(
            {
                'status' : 200,
                'message' : 'Already logged in',
                'redirect_to' : reverse('dashboard'),
            },
            status = 200
        )
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return JsonResponse(
                {
                    'status' : 200,
                    'message' : 'Logged in Successfully',
                    'redirect_to' : reverse('dashboard'),
                },
                status = 200
            )
        else:
            return JsonResponse(
                {
                    'status' : 401,
                    'message' : 'Incorrect username or password',
                    'redirect_to' : reverse('login'),
                },
                status = 401
            )
        
    return JsonResponse(
        {
                'status' : 200,
                'message' : 'Fill in username and password',
        },
            status = 200
        )

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        message = "Logged out successfully"
    else:
        message = "User already logged out"
        
    return JsonResponse(
        {
            "message": message,
            "redirect_to": reverse("login")
        },
        status=200
    )


User = get_user_model()


def user_detail(request, pk):
    user = get_object_or_404(User, id=pk)

    # Stats
    posts_count = Post.objects.filter(author=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    # Recent posts
    recent_posts = list(
        Post.objects.filter(author=user)
        .order_by("-created_at")[:5]
        .values("id", "title", "created_at")
    )

    for post in recent_posts:
        post["link"] = reverse("post_detail", kwargs={"pk": post["id"]})

    # Recent comments on user's posts
    recent_comments = list(
        Comment.objects
        .filter(post__author=user)
        .select_related("post", "user")
        .order_by("-posted_at")[:5]
        .values(
            "id",
            "content",
            "posted_at",
            "user__username",
            "post__id",
            "post__title"
        )
    )

    for comment in recent_comments:
        # link to the post being commented
        comment["post_link"] = reverse("post_detail", kwargs={"pk": comment["post__id"]})
        # link to the commenter's profile
        comment["user_link"] = reverse("user_detail", kwargs={"pk": comment["user__id"]})

    # Recent followers
    recent_followers = list(
        Follow.objects
        .filter(following=user)
        .select_related("follower")
        .order_by("-followed_at")[:5]
        .values(
            "id",
            "follower__username",
            "followed_at"
        )
    )

    for follower in recent_followers:
        follower["user_link"] = reverse("user_detail", kwargs={"pk": follower["follower__id"]})

    return JsonResponse({
        "user": {
            "username": user.username,
            "followers_count": followers_count,
            "following_count": following_count,
            "posts_count": posts_count,
            "joined_at": getattr(user, "joined_at", user.joined_at).isoformat(),
        },
        "recent_posts": recent_posts,
        "recent_comments": recent_comments,
        "recent_followers": recent_followers,
    }, safe=False, status = 200)
    

def user_followers (request, pk):
    pass

def user_following (request, pk):
    pass

def user_posts (request, pk):
    pass

def feed (request, pk):
    pass

def post_detail (request, pk):
    pass

@login_required
def dashboard(request):
    return JsonResponse({
        "links": {
            "profile": reverse("user_detail", kwargs={"pk": request.user.id}),
            "feed": reverse("feed"),
            "search": reverse("search"),
            "my_posts": reverse("my_posts"),
            "logout": reverse("logout"),
        }
    })