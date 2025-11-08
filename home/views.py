from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Project, ImpactCounter, Milestone, Feedback, ContactMessage, Donation
from decimal import Decimal

# Create your views here.
def index(request):
    """
    Home / Index Page View:
    - Displays active donation projects
    - Shows overall impact counters
    """

    # Fetch active projects (status='active')
    projects = Project.objects.filter(status='active').order_by('-created_at')

    # Fetch impact counters
    impact_qs = ImpactCounter.objects.all()

    # Format impact keys for readability
    # Example: "Total Donations" instead of "total_donations"
    impact = {}
    for counter in impact_qs:
        formatted_name = counter.name.title().replace("_", " ")
        impact[formatted_name] = counter.value

    # Render the template with formatted impact labels
    return render(request, "index.html", {
        "projects": projects,
        "impact": impact,
    })





def about(request):
    # Fetch impact counts
    impact = {
        'meals_served': ImpactCounter.objects.filter(name__icontains='Meals Served').first().value
                        if ImpactCounter.objects.filter(name__icontains='Meals Served').exists() else 0,
        'trees_planted': ImpactCounter.objects.filter(name__icontains='Trees Planted').first().value
                        if ImpactCounter.objects.filter(name__icontains='Trees Planted').exists() else 0,
        'families_helped': ImpactCounter.objects.filter(name__icontains='Families Helped').first().value
                        if ImpactCounter.objects.filter(name__icontains='Families Helped').exists() else 0,
        'projects_funded': ImpactCounter.objects.filter(name__icontains='Projects Funded').first().value
                        if ImpactCounter.objects.filter(name__icontains='Projects Funded').exists() else 0,
    }

    # Fetch milestones (latest first)
    milestones = Milestone.objects.all().order_by('-date_achieved')[:10]

    # Fetch testimonials (optional: to show on About page)
    testimonials = Feedback.objects.filter(feedback_type__in=['donor','general']).order_by('-created_at')[:6]
    
    return render(request, "about.html", {
        'impact': impact,
        'milestones': milestones,
        'testimonials': testimonials,
    })

def projects(request):
    """
    Display projects categorized as ongoing or completed, along with distinct project categories.
    """
    ongoing_projects = Project.objects.filter(status='active').order_by('-created_at')
    completed_projects = Project.objects.filter(status='completed').order_by('-end_date')
    categories = Project.objects.values_list('category', flat=True).distinct().exclude(category__isnull=True).exclude(category__exact='')

    context = {
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'categories': categories,
    }

    return render(request, 'projects.html', context)

def impacts(request):
    # Fetch impact counters
    impact_counters = ImpactCounter.objects.all()

    # Fetch all projects
    projects = Project.objects.all()

    # Calculate progress percentage for each project
    for project in projects:
        try:
            project.progress_percent = (project.collected_amount / project.goal_amount) * 100 if project.goal_amount else 0
        except ZeroDivisionError:
            project.progress_percent = 0

    # Fetch milestones / achievements
    milestones = Milestone.objects.select_related('project').all()

    return render(request, 'impacts.html', {
        'impact_counters': impact_counters,
        'projects': projects,
        'milestones': milestones,
    })

def feedback(request):
    if request.method == 'POST':
        # Fetch POST data
        name = request.POST.get('name') or None
        email = request.POST.get('email') or None
        feedback_type = request.POST.get('feedback_type', 'general')
        feedback_text = request.POST.get('feedback_text', '').strip()
        rating = request.POST.get('rating') or 5

        # Ensure rating is integer
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                rating = 5
        except ValueError:
            rating = 5

        # Validate feedback text
        if not feedback_text:
            messages.error(request, "Feedback cannot be empty.")
            return redirect('feedback')

        # Create Feedback entry
        Feedback.objects.create(
            name=name,
            email=email,
            feedback_type=feedback_type,
            feedback_text=feedback_text,
            rating=rating
        )

        messages.success(request, "Thank you! Your feedback has been submitted.")
        return redirect('feedback')  # Redirect to same page to show updated testimonials

    # GET request: fetch all feedbacks to display
    feedbacks = Feedback.objects.all()  # Ordered by model's Meta ordering
    return render(request, 'feedback.html', {'feedbacks': feedbacks})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', 'general')
        message_text = request.POST.get('message')

        # Save to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text
        )

        # Success message
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')  # Update with your URL name for contact page

    return render(request, 'contact.html')





def donate(request):
    projects = Project.objects.filter(status='active')

    if request.method == 'POST':
        project_id = request.POST.get('project')
        project = get_object_or_404(Project, id=project_id)

        # Get donation amount as Decimal
        amount_str = request.POST.get('custom_amount') or '0'
        try:
            amount = Decimal(amount_str)
        except:
            amount = Decimal('0')

        if amount <= 0:
            return render(request, 'donate.html', {
                'projects': projects,
                'error': "Please enter a valid donation amount."
            })

        donor_name = request.POST.get('name')
        donor_email = request.POST.get('email')
        donor_phone = request.POST.get('phone')
        donor_address = request.POST.get('address')
        recurring = True if request.POST.get('recurring') else False
        anonymous = True if request.POST.get('anonymous') else False
        payment_method = request.POST.get('payment_method', 'bank')

        # Create Donation
        donation = Donation.objects.create(
            project=project,
            donor_name=donor_name,
            donor_email=donor_email,
            donor_phone=donor_phone,
            donor_address=donor_address,
            amount=amount,
            recurring=recurring,
            anonymous=anonymous,
            payment_method=payment_method,
            confirmed=False
        )

        # Update project collected amount
        # project.collected_amount += amount
        # project.save()

        # Display success message
        messages.success(request, f"Thank you {donor_name}! Your donation of ₹{amount} has been received.")


        return redirect('donate')

    return render(request, "donate.html", {'projects': projects})


def policy(request):
    return render(request, "policy.html")

def terms(request):
    return render(request, "terms.html")