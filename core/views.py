from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.db.models import Count
from django.db.models import Q
from django.views import View
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404, redirect
from .models import BlogModel, CommentModel
from .forms import CommentForm
from django.utils.timezone import now
from datetime import datetime
from .forms import CommentForm
from .models import BlogModel


class LoginView(auth_views.LoginView):
    template_name = 'core/form.html'    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        context['form_title'] = 'Login'
        context['form_btn'] = 'Login'
        return context
    

class RegisterView(View):
    template_name = 'core/form.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})


class HomePageView(ListView):
    model = BlogModel
    template_name = 'core/index.html'
    context_object_name = 'blogs'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        sorted_by = self.request.GET.get('sorted_by')

        # Start with the default queryset
        queryset = BlogModel.objects.all()

        # Filter the blogs based on title, content, or author if there's a search query
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query)
            )

        # Set the blog order
        ordering = ['-created_at', '-views']
        if sorted_by == 'views':
            ordering = ['-views']
        elif sorted_by == 'likes':
            queryset = queryset.annotate(likes_count=Count('likemodel')).order_by('-likes_count', '-views')

        # Apply the final ordering to the queryset
        if not sorted_by == 'likes':
            queryset = queryset.order_by(*ordering)

        return queryset


class BlogDetailView(DetailView):
    model = BlogModel
    template_name = 'core/blog_detail.html'
    context_object_name = 'blog'

    def get(self, request, *args, **kwargs):
        # Get the blog object
        blog = self.get_object()

        # Increment the views count by 1
        blog.views += 1
        blog.save()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        current_time = now()
        # Filter comments that have no parent (root comments)
        root_comments = blog.commentmodel_set.filter(parent__isnull=True).order_by('-created_at')
        for comments in root_comments:
            time_difference = current_time - comments.created_at
            days = time_difference.days
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            # Attach the time difference string to the comment object
            if days > 0:
                comments.time_difference = f"{days} days ago"
            elif hours > 0:
                comments.time_difference = f"{hours} hours  ago"
            elif minutes > 5:
                comments.time_difference = f"{minutes} minutes ago"
            else:
                comments.time_difference = "Just now"

        context['title'] = blog.title
        context['comment_form'] = CommentForm()
        context['root_comments'] = root_comments  # Pass root comments to the template
        return context



class BlogCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BlogModel
    template_name = 'core/form.html'
    fields = ['title', 'content', 'media']
    success_message = 'The blog post was successfully posted.'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Make Blog'
        context['form_title'] = 'Make Blog'
        context['form_btn'] = 'Post'
        context['with_media'] = True
        return context
    

class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = BlogModel
    template_name = 'core/form.html'
    fields = ['title', 'content', 'media']
    success_message = 'The blog post was successfully updated.'

    def test_func(self):
        # Check if the authenticated user is the author of the blog
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Blog'
        context['form_title'] = 'Update Blog'
        context['form_btn'] = 'Update'
        context['with_media'] = True
        return context


class BlogDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = BlogModel
    template_name = 'core/blog_delete.html'
    success_url = reverse_lazy('home')  # Redirect to the home page after deletion
    context_object_name = 'blog'
    success_message = 'The blog post was successfully deleted.'
    
    def test_func(self):
        # Check if the authenticated user is the author of the blog
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Blog'
        return context

class CommentCreateView(FormView):
    form_class = CommentForm

    def form_valid(self, form):
        # Get the blog ID and parent comment ID from the form
        blog_id = self.kwargs['blog_id']
        parent_comment_id = self.request.POST.get('parent_id')

        blog = get_object_or_404(BlogModel, id=blog_id)

        # If a parent comment ID is provided, get the parent comment, else None
        parent_comment = None
        if parent_comment_id:
            parent_comment = get_object_or_404(CommentModel, id=parent_comment_id)

        # Create the new comment
        new_comment = CommentModel(
            text=form.cleaned_data['text'],
            blog=blog,
            user=self.request.user,
            parent=parent_comment  # Link the reply to the parent comment if exists
        )
        new_comment.save()

        return redirect('blog_detail', pk=blog_id)
