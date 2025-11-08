from django.db import models

# =======================
# Project & Related Models
# =======================
class Project(models.Model):
    # Basic Info
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, null=True)

    # Donation / Funding Info
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)       # Target in PKR
    collected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='PKR')

    # Dates
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)

    # Status & Category
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('upcoming', 'Upcoming'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    category = models.CharField(max_length=100, blank=True, null=True)

    # Optional Extra Fields
    location = models.CharField(max_length=200, blank=True, null=True)
    impact_metrics = models.JSONField(blank=True, null=True)  # Example: {'meals_served': 1000}

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


class ImpactCounter(models.Model):
    """
    Stores key impact stats like Meals Served, Trees Planted, Families Helped, Projects Funded.
    """
    name = models.CharField(max_length=100, unique=True)
    value = models.PositiveIntegerField(default=0)
    icon_class = models.CharField(max_length=50, blank=True)  # e.g., 'bi-egg-fried'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Impact Counter"
        verbose_name_plural = "Impact Counters"

    def __str__(self):
        return f"{self.name}: {self.value}"


class Milestone(models.Model):
    """
    Represents a milestone or achievement for a project or platform.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_achieved = models.DateField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='milestones')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Milestone"
        verbose_name_plural = "Milestones & Achievements"
        ordering = ['-date_achieved']

    def __str__(self):
        return f"{self.title} ({self.date_achieved})"


# =======================
# Feedback & Contact Models
# =======================
class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('beneficiary', 'Beneficiary'),
        ('donor', 'Donor'),
        ('general', 'General'),
    ]
    RATING_CHOICES = [(i, f"{i} ⭐") for i in range(1, 6)]

    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    feedback_text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.feedback_type} feedback by {self.name or 'Anonymous'}"


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General'),
        ('donation', 'Donation'),
        ('feedback', 'Feedback'),
        ('partnership', 'Partnership'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


# =======================
# Donation Model
# =======================
class Donation(models.Model):
    PAYMENT_METHODS = [
        ('bank', 'Bank Transfer'),
        ('ewallet', 'E-Wallet (JazzCash/EasyPaisa)'),
        ('cash', 'Cash / Cheque'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    donor_name = models.CharField(max_length=200)
    donor_email = models.EmailField()
    donor_phone = models.CharField(max_length=20, blank=True, null=True)
    donor_address = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recurring = models.BooleanField(default=False)
    anonymous = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    confirmed = models.BooleanField(default=False)  # For manual verification
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} - {self.project.title} - ₹{self.amount}"
