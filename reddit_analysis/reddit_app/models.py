from django.db import models

class RedditPost(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    author = models.CharField(max_length=100)
    subreddit = models.CharField(max_length=100)
    score = models.IntegerField()
    sentiment = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title