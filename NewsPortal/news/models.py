from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from datetime import datetime


class Appointment(models.Model):
    time_creation = models.DateField(
        default=datetime.utcnow,
    )
    author = models.CharField(
        max_length=200
    )
    text = models.TextField()

    def __str__(self):
        return f'{self.client_name}: {self.message}'


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete = models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default = 0)

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postRating = Sum('rating'))
        pRat = postRat.get('postRating') or 0

        commentRat = self.authorUser.comment_set.all().aggregate(commentRating = Sum('ratingComm'))
        cRat = commentRat.get('commentRating') or 0

        self.ratingAuthor = pRat * 3 + cRat
        self.save()

    def __str__(self):
        return self.authorUser.username

class Category(models.Model):
    name = models.CharField(max_length = 255, unique = True)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete = models.CASCADE)

    ARTICLE = 'AR'
    NEWS = 'NW'

    CATEGORY_CHOICES = [
        (ARTICLE, 'СТАТЬЯ'),
        (NEWS, 'НОВОСТЬ')
    ]

    category_type = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    time_creation = models.DateTimeField(auto_now_add = True)
    post_category = models.ManyToManyField(Category, through = 'PostCategory')
    title = models.CharField(max_length = 128)
    text = models.TextField()
    rating = models.SmallIntegerField(default = 0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete = models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.postThrough.title} - {self.categoryThrough.name}'


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete = models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete = models.CASCADE)
    textComment = models.TextField()
    timeComment = models.DateTimeField(auto_now_add = True)
    ratingComm = models.SmallIntegerField(default = 0)

    def like(self):
        self.ratingComm += 1
        self.save()

    def dislike(self):
        self.ratingComm -= 1
        self.save()

    def __str__(self):
        return f'{self.commentPost.title} - {self.commentUser.username}'