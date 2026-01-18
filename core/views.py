from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm
from .models import Tickets
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from google import genai
from google.genai import types
from django.conf import settings

def index(request):
    return render(request, 'core/index.html')

def about_triprep(request):
    """Render a simple About page (Coming Soon)."""
    return render(request, 'core/about_triprep.html')

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
            auth_login(request, user)
            # Preserve the first name across the redirect so dashboard can greet the user
            request.session['first_name'] = first_name
            return redirect('core:dashboard')
    else:
        form = SignupForm()
    
    return render(request, 'core/signup.html', {'form': form})

def dashboard(request):
    print("Dashboard accessed by user:", request.user)
    if request.user.is_anonymous:
        print("User is anonymous and not logged in, redirecting to login")
        return redirect('core:login')
    # Get first_name from session (set during signup) or fall back to the user's first_name
    first_name = request.session.pop('first_name', None) or request.user.first_name
    return render(request, 'core/dashboard.html', {'first_name': first_name})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            print("User logged in:", form.get_user())
            return redirect('core:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    from django.contrib.auth import logout
    print("Logging out user:", request.user)
    logout(request)
    return redirect('core:index')

def tickets(request):
    if request.user.is_anonymous:
        return redirect('core:login')
    tickets = Tickets.objects.filter(user=request.user)
    return render(request, 'core/tickets.html', {'tickets': tickets})

def add_ticket(request):
    print(f"Request Method = {request.method}")
    if request.user.is_anonymous:
        return redirect('core:login')
    return render(request, 'core/add_ticket.html')

def process_file(file):
    file_pdf = file.read()

    # load API key from settings
    genai_api_key = settings.GENAI_API_KEY
    client = genai.Client(api_key=genai_api_key)
    prompt = "Summarize this document"
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(
            data=file_pdf,
            mime_type='application/pdf',
        ),
        prompt])
    print(response.text)

@require_http_methods(["POST"])
def create_ticket(request):
    if request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Process your file here
        print(f"File name: {uploaded_file.name}")
        print(f"File size: {uploaded_file.size}")
        process_file(uploaded_file)
        return JsonResponse({
                'status': 'success',
                'message': 'File uploaded successfully',
                'filename': uploaded_file.name,
            }, status=200)
    else:
        return JsonResponse({
                'status': 'error',
                'message': 'No file uploaded'
            }, status=400)

def process_ticket_pdf(request):
    print(f"Request Method = {request.method}")
    return