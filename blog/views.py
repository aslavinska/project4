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
from django.contrib import messages


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
        return reverse("post_detail", kwargs={"slug": slug})


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'postdelete.html'
    success_url = "/blog"


def success(request):
    return render(request, 'success.html')


def about(request):
    return render(request, 'about.html', {})


def home(request):
    return render(request, 'home.html', {})


def onlinetime(request):
    return render(request, 'onlinetime.html', {})


def commission(request):
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
            return redirect('commission')

        if style == None:
            messages.success(request, "Please Select A Style!")
            return redirect('commission')

        print("This is working")

        commission = Commission.objects.create(
            service=service,
            style=style,
            day=day,
            user=user,
        )

        return redirect('bookingSubmit')

    return render(request, 'commission.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
    })


def bookingSubmit(request):
    user = request.user
    service = request.session.get('service')
    style = request.session.get('style')

    if request.method == 'POST':
        return redirect('commission')

    return render(request, 'bookingSubmit.html')


def validWeekday(days):
    # Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range(0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Monday' or y == 'Saturday' or y == 'Wednesday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays


def isWeekdayValid(x):
    validateWeekdays = []
    for j in x:
        if Commission.objects.filter(day=j).count() < 10:
            validateWeekdays.append(j)
    return validateWeekdays


def userPanel(request):
    user = request.user
    commissions = Commission.objects.filter(user=user).order_by('day')
    return render(request, 'userPanel.html', {
        'user': user,
        'commissions': commissions,
    })


def userUpdate(request, id):
    commission = Commission.objects.get(pk=id)
    userdatepicked = commission.day
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')

    # 24h if statement in template:
    delta24 = (userdatepicked).strftime(
        '%Y-%m-%d') >= (today + timedelta(days=1)).strftime('%Y-%m-%d')
    # Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)

    # Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')

        # Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service

        return redirect('userUpdateSubmit', id=id)

    return render(request, 'userUpdate.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
        'delta24': delta24,
        'id': id,
    })


def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y


def userUpdateSubmit(request, id):
    user = request.user
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')
    service = request.session.get('service')

    # Only show the time of the day that has not been selected before and the time he is editing:

    commission = Commission.objects.get(pk=id)

    if request.method == 'POST':

        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Saturday' or date == 'Wednesday':
                    if Commission.objects.filter(day=day).count() < 11:

                        CommissionForm = Commission.objects.filter(pk=id).update(
                            user=user,
                            service=service,
                            day=day,

                        )

                        messages.success(
                            request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                messages.success(
                    request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service!")
        return redirect('userPanel')

    return render(request, 'userUpdateSubmit.html', {
        'id': id,
    })
