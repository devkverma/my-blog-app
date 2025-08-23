from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.core.exceptions import ValidationError

# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)
    
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Assign custom manager
    objects = CustomUserManager()

class BlogUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_link = models.URLField(max_length=200, blank=True)
    profile_pic = models.URLField(max_length=200, blank=True)
    DateOfBirth = models.DateField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'author', null = False)
    title = models.CharField(max_length= 150,null= False)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.TextField(null= True)
    content = models.TextField(null=False)
    likes = models.IntegerField(null= True, blank = True)

    def __str__(self):
        return self.author.username + " - " + self.title

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'like_user', null = False)
    liked_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " liked " + self.post.title + " by " + self.post.author.username
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'comment_user', null = False)
    ParentCommentID = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(null=False)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.post.title}"
    
    def clean(self):
        if self.ParentCommentID is not None and self.post != self.ParentCommentID.post:
            raise ValidationError("Bad reply to comment")

class Follow (models.Model):
    followers = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'follower', null = False)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name= 'following', null = False)
    followed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.followers.username + " following " + self.following.username
    
    class Meta:
        unique_together = ('followers', 'following')

    def clean(self):
        if self.followers == self.following:
            raise ValidationError("A user cannot follow themselves.")

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
