from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic
from .models import Post

class PostListView(generic.ListView):
    queryset = Post.published.all()
    paginate_by = 3
    context_object_name ='posts'
    template_name = 'blog/post/list.html'
    

def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404('No Post found.')
    
    post_data = get_object_or_404(Post, status=Post.Status.PUBLISHED, 
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day=day)
    return render(request, 'blog/post/detail.html', {'post':post_data})
