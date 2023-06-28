from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, reverse, redirect
from datetime import datetime, timedelta
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib import auth
from .models import *
from .forms import CommentForm, ContactForm



class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "blog.html"
    paginate_by = 6


class PostDetail(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )
    
    def post(self, request, slug, *args, **kwargs):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )

class PostLike(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))

class PostEditView(UpdateView):
    model = Post
    fields = ['content']
    template_name = 'postedit.html'
    def get_success_url(self):
        slug = self.kwargs["slug"]
        return reverse("post_detail", kwargs = {"slug":slug})


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'postdelete.html'
    success_url = "/blog"

def contact(request):
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
            # Process the form data
                send_mail('Subject here', 'Here is the message.', 'from@example.com', ['to@example.com'], fail_silently=False)
                return redirect('success')
        else:
            form = ContactForm()
            return render(request, 'contact.html', {'form': form})  

        return render(request, 'contact.html', {'form': form})

def success(request):
     return render(request, 'success.html')


def about(request):
    return render(request, 'about.html',{})


def home(request):
    return render(request, 'home.html',{})


def onlinetime(request):
    return render(request, 'onlinetime.html',{})


def booking(request):
    weekdays = validWeekday(22)
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        style = request.POST.get('style')
        day = request.POST.get('day')
        user = request.user
        print(service, style, user)
        
        if service == None:
            messages.success(request, "Please Select A Service!")
            return redirect('booking')

        if style == None:
            messages.success(request, "Please Select A Style!")
            return redirect('booking')
        

        print("This is working")

        appointment = Appointment.objects.create(
               service = service,
               style= style,
               day = day,
               user = user,
            )
        #appointment.save(force_insert=True)
        print(appointment)
        return redirect('bookingSubmit')

    return render(request, 'booking.html', {
            'weekdays':weekdays,
            'validateWeekdays':validateWeekdays,
        })

def bookingSubmit(request):
    user = request.user

    #Get stored data from django session:
    service = request.session.get('service')
    style = request.session.get('style')
    
    if request.method == 'POST':
        return redirect('booking')

    return render(request, 'bookingSubmit.html')

def validWeekday(days):
    #Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range (0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Monday' or y == 'Saturday' or y == 'Wednesday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays
    
def isWeekdayValid(x):
    validateWeekdays = []
    for j in x:
        if Appointment.objects.filter(day=j).count() < 10:
            validateWeekdays.append(j)
    return validateWeekdays