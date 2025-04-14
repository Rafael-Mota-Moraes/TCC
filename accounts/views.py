from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import UserRegistrationForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Conta criada para {username}! Agora você pode fazer login."
            )
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})
