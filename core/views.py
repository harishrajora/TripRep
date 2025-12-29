from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html')


def about_triprep(request):
    """Render a simple About page (Coming Soon)."""
    return render(request, 'core/about_triprep.html')

def signup(request):
    """Render a simple Signup page (Coming Soon)."""
    return render(request, 'core/about_triprep.html')

