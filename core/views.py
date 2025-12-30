from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import SignupForm


def index(request):
    return render(request, 'core/index.html')


def about_triprep(request):
    """Render a simple About page (Coming Soon)."""
    return render(request, 'core/about_triprep.html')

# def signup(request):
#     """Render a simple Signup page (Coming Soon)."""
#     return render(request, 'core/signup.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create the user
            first_name=form.cleaned_data['first_name']
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # Using email as username
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            # Log the user in automatically
            login(request, user)
            return render(request, 'core/dashboard.html', {'first_name': first_name})
    else:
        form = SignupForm()
    
    return render(request, 'core/signup.html', {'form': form})

def dashboard(request):
    return render(request, 'core/dashboard.html')
