from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic
from django.views.decorators.http import require_POST
from django.db.models import Count
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag


class PostListView(generic.ListView):
    paginate_by = 3
    context_object_name ='posts'
    template_name = 'blog/post/list.html'
    
    def get_queryset(self):
        queryset = Post.published.all()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = Post.published.filter(tags__in=[tag])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get('tag_slug')
        
        if tag_slug:
            context['tag'] = get_object_or_404(Tag, slug=tag_slug)
        else:
            context['tag'] = None

        return context


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
    # comments = Comment.objects.filter(active=True)
    comments = post_data.comments.filter(active=True)
    form = CommentForm()

    # List of similar posts
    post_tags_ids = post_data.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post_data.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]

    return render(
        request, 
        'blog/post/detail.html', 
        {
            'post':post_data, 
            'comments':comments, 
            'form':form,
            'similar_posts': similar_posts
        }
    )


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