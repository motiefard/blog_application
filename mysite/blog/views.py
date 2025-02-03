from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic
from django.views.decorators.http import require_POST
from .models import Post
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail


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


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status= Post.Status.PUBLISHED)
    sent = False
    
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                # from_email=cd['email'],
                recipient_list=[cd['to']]
            )
            sent = True

    else:
        form = EmailPostForm()
    
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent':sent} )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)   # Create a Comment object without saving it to the database
        comment.post = post     # assign post to comment
        comment.save()

    return render(request, 'blog/post/comment.html', {'post':post, 'form':form, 'comment':comment})