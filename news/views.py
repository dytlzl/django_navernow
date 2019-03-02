from django.shortcuts import render, get_object_or_404
from .models import Post


def timeline(request):
    posts = Post.objects.all().order_by('date').reverse
    return render(request, 'news/timeline.html', {'posts': posts})


def article(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'news/article.html', {'post': post})
