from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import UserRegisterForm


def register_view(request):

    if request.method == "POST":

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("books:list")

    else:

        form = UserRegisterForm()

    return render(
        request,
        "users/register.html",
        {"form": form},
    )