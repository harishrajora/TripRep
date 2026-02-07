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
from django.utils import timezone
from django.db.models import Sum, Count

def index(request):
    return render(request, 'core/index.html')

def profile(request):
    if request.user.is_anonymous:
        return redirect('core:login')
    return render(request, 'core/profile.html', {'message': 'Update Profile'})

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
    tickets = Tickets.objects.filter(user=request.user).order_by('-uploaded_at')
    # print(tickets)
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
    prompt = "Check whether this is a ticket of any kind or not. If it is a ticket, your response should" \
    "start with 'Yes, this is a ticket. Then list down the following things in a JSON format: \n" \
    "1. Source \n 2. Destination \n 3. Ticket Type \n 4. Description \n 5. Date of Journey \n 6. Title \n " \
    "7. Booked Through \n"
    "There are few things to remember while extracting the information. The 'Ticket Type' should have value strctly" \
    " as one of the following: Flight, Bus, Train, Ferry, Other. No other word should be used in addition to this. "
    "The 'Booked Through' field means the website"
    "used for booking the ticket. For ex, Agoda or Booking.com."
    " The Title field should be a short title for the " \
    "ticket. If any information is missing, use 'Not Found' as the value for that field. the description should" \
    "not exceed 100 words. If it is not a ticket, response should start with 'No, it's not a ticket'. In this" \
    "case, you don't need to populate the values but return only a single sentence."
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(
            data=file_pdf,
            mime_type='application/pdf',
        ),
        prompt])
    print("Response from GenAI received")
    return response.text

@require_http_methods(["POST"])
def create_ticket(request):
    if request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # Process your file here
        print(f"File name: {uploaded_file.name}")
        print(f"File size: {uploaded_file.size}")
        response = process_file(uploaded_file)
        json_response = response.split("{")
        if json_response[0].strip().startswith("Yes,"):
            print("The uploaded file is recognized as a ticket.")
            # Reconstruct the JSON part
            json_part = "{" + "{".join(json_response[1:])
            json_part = json_part[:-3]
            import json
            ticket_data = json.loads(json_part)
            return JsonResponse({
                    'status': 'success',
                    'message': 'File uploaded successfully',
                    'filename': uploaded_file.name,
                    'ticket_data': ticket_data
                }, status=200)
        else:
            return JsonResponse({
                    'status': 'error',
                    'message': 'The uploaded file is not recognized as a ticket.',
                }, status=400)
    else:
        return JsonResponse({
                'status': 'error',
                'message': 'No file uploaded'
            }, status=404)

def process_ticket_pdf(request):
    print(f"Request Method = {request.method}")
    return

def save_ticket(request):
    if request.method == 'POST':
        if request.user.is_anonymous:
            return redirect('core:login')
        title = request.POST.get('title')
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        description = request.POST.get('description')
        date_of_journey = request.POST.get('date_of_journey')
        ticket_type = request.POST.get('ticket_type_dropdown')
        booked_through = request.POST.get('booked_through')
        ticket_pdf = request.FILES.get('ticket_pdf')
        amount_paid = request.POST.get('amount_paid', '0.00')
        # only keep digits and decimal point
        amount_paid = ''.join(c for c in amount_paid if (c.isdigit() or c == '.'))
        if "." not in amount_paid:
            amount_paid += ".00"
        # remove any leading zeros
        if amount_paid.startswith('0'):
            amount_paid = amount_paid.lstrip('0')
            if amount_paid == '' or amount_paid.startswith('.'):
                amount_paid = '0' + amount_paid
        
        # limit to 8 characters
        if len(amount_paid) > 8:
            amount_paid = amount_paid[:8]
        print(ticket_pdf)
        ticket = Tickets(
            user=request.user,
            title=title,
            ticket_file=ticket_pdf,
            source=source,
            destination=destination,
            description=description,
            date_of_journey=date_of_journey,
            ticket_type=ticket_type,
            booked_through=booked_through,
            amount_paid=amount_paid
        )
        ticket.save()
        print(f"Ticket '{title}' saved for user {request.user.username}")
        return redirect('core:tickets')
    else:
        return redirect('core:add_ticket')


def view_ticket(request, ticket_id):
    if request.user.is_anonymous:
        return redirect('core:login')
    try:
        ticket = Tickets.objects.get(id=ticket_id, user=request.user)
        if ticket.user != request.user:
            return redirect('core:tickets')
    except Tickets.DoesNotExist:
        return redirect('core:tickets')
    return render(request, 'core/view_ticket.html', {'ticket': ticket})

def delete_ticket(request, ticket_id):
    if request.user.is_anonymous:
        return redirect('core:login')
    try:
        ticket = Tickets.objects.get(id=ticket_id, user=request.user)
        if ticket.user != request.user:
            return redirect('core:tickets')
        ticket.delete()
        print(f"Ticket with ID {ticket_id} deleted for user {request.user.username}")
    except Tickets.DoesNotExist:
        print(f"Ticket with ID {ticket_id} does not exist or does not belong to user {request.user.username}")
    return redirect('core:tickets')

def statistics(request):
    if request.user.is_anonymous:
        return redirect('core:login')
    
    tickets = Tickets.objects.filter(user=request.user)
    
    total_tickets = tickets.count()
    total_amount_spent = tickets.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0.00
    
    # Tickets by type
    ticket_types = tickets.values('ticket_type').annotate(count=Count('ticket_type'))
    ticket_type_data = {item['ticket_type']: item['count'] for item in ticket_types}
    
    context = {
        'total_tickets': total_tickets,
        'total_amount_spent': total_amount_spent,
        'ticket_type_data': ticket_type_data,
    }
    
    return render(request, 'core/statistics.html', context)


def update_profile(request):
    if request.user.is_anonymous:
        return redirect('core:login')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        User.objects.filter(email=user.email).update(first_name=first_name, last_name=last_name)
        print(f"Profile updated for user {user.username}")
        return render(request, 'core/profile.html', {'message': 'Profile updated successfully'})
    
    return render(request, 'core/profile.html', {'message': 'Profile update failed'})

def reservations(request):
    if request.user.is_anonymous:
        return redirect('core:login')
    return render(request, 'core/reservations.html')

def add_reservation(request):
    if request.user.is_anonymous:
        return redirect('core:login')
    return render(request, 'core/add_reservation.html')