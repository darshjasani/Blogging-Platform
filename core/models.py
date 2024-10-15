from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.utils.timezone import now
from datetime import timedelta

class BlogModel(models.Model):
    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    media = models.ImageField(upload_to='blog_media/', blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('home')


class CommentModel(models.Model):
    blog = models.ForeignKey(BlogModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)  # For nested comments
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"

    @property
    def time_difference(self):
        current_time = now()
        time_difference = current_time - self.created_at
        days = time_difference.days
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            return f"{days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 5:
            return f"{minutes} minutes ago"
        else:
            return "Just now"

class LikeModel(models.Model):
    blog = models.ForeignKey(BlogModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} liked {self.blog.title}"
