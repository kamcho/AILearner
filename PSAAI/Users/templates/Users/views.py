from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.shortcuts import render,redirect
from django.views.generic import DetailView,CreateView,UpdateView,DeleteView,ListView,TemplateView
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegister,ProfileUpdate,UserUpdate
from .models import Profile,About
from django.urls import reverse
# from .models import Posts

from Home.models import Posts,AdminPosts



from django.contrib import messages
# Create your views here.
def Register(request):

    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account Created for {username}')
            return redirect('home')
    else:
        form=UserRegister()
    return render(request,'Users/Register.html',{'form':form})


def Home(request):
    return render(request,'Users/Home.html')
# def posts(request):
#     context={'poster':Posts.objects.filter(author=request.user).values()}
# class MyProfile(ListView,LoginRequiredMixin):
#     template_name = 'Users/profiles.html'
#     model = Posts
#     # context_object_name='poster'
#     def get_queryset(self,request):
#         poster=super.get_queryset(request)
#         return poster.filter(author=request.user)
def MyProfile(request):
    user=request.user
    user_posts=Posts.objects.filter(author=request.user)
    template='Users/profiles.html'
    return render(request,template,{'user_posts':user_posts,'user':user})
def MyAbout(request):
    # user=request.user
    # user_posts=Posts.objects.filter(author=request.user)
    template='Users/about.html'
    return render(request,template)

from django.urls import reverse_lazy
class update_profile(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=Profile
    template_name='Users/update_profile.html'
    fields=['phone','gender','pic']
    def form_valid(self,form):
        form.instance.user
        return super().form_valid(form)
    def test_func(self):
        detail = self.get_object()
        if self.request.user == detail.user :
            return True
        return False

    def get_absolute_url(self):
        return reverse('profile')


class update_about(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=About
    template_name='Users/update_about.html'
    fields=['music','religion','team','hobby']
    def form_valid(self,form):
       
        form.instance.user
        return super().form_valid(form)
    def test_func(self):
        detail = self.get_object()
        if self.request.user == detail.user :
            return True
        return False

    def get_absolute_url(self):
        return reverse('profile')

#
# def adminposts(request):
#     user=self.request.user
#     print(user)
#
#     context={'poosts':Posts.objects.filter(id=1)}
#
#     return render(request,'Home/base.html',context)
class Home(ListView):
    template_name = 'Users/Home.html'
    model = AdminPosts
    ordering = ['-date']
    context_object_name = 'adminposts'

# class DeleteProfile(DeleteView,LoginRequiredMixin,UserPassesTestMixin):
#     template_name = 'Users/DeleteProfile.html'
#     model = ''
#     pass
#
#
