from django.db import models
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 1)  # Assuming 1 is the AdminUser

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        (1, "AdminUser"),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    user_type = models.IntegerField(default=1, choices=USER_TYPE_CHOICES)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()  # Custom manager for handling user creation

    def __str__(self):
        return self.email

class AdminUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin: {self.user.email}"

class Document(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Document {self.id} - {self.user.email} ({self.status})"


User = get_user_model()

class ProcessedDocument(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed')
    )

    # Existing fields
    original_text = models.TextField()
    improved_text = models.TextField()
    grammar_suggestions = models.JSONField(blank=True, null=True)
    style_suggestions = models.JSONField(blank=True, null=True)
    clarity_improvements = models.JSONField(blank=True, null=True)
    tone_analysis = models.JSONField(blank=True, null=True)
    consistency_score = models.FloatField(blank=True, null=True)
    document_stats = models.JSONField(blank=True, null=True)
    processing_time = models.DateTimeField(default=now)

    # New fields needed for full functionality
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_documents')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_suggestions = models.JSONField(blank=True, null=True, default=list)

    class Meta:
        ordering = ['-processing_time']

    def __str__(self):
        return f"ProcessedDocument {self.id} - {self.processing_time}"

    def apply_suggestion(self, suggestion):
        """
        Apply a suggestion to the document and record it
        """
        if suggestion.get('original') and suggestion.get('suggested'):
            self.improved_text = self.improved_text.replace(
                suggestion['original'],
                suggestion['suggested']
            )
            
            if self.applied_suggestions is None:
                self.applied_suggestions = []
            
            self.applied_suggestions.append(suggestion)
            self.save()

    def get_remaining_suggestions(self):
        """
        Get suggestions that haven't been applied yet
        """
        applied = set(sug.get('id') for sug in (self.applied_suggestions or []))
        
        all_suggestions = {
            'grammar': self.grammar_suggestions or [],
            'style': self.style_suggestions or [],
            'clarity': self.clarity_improvements or []
        }
        
        return {
            k: [s for s in v if s.get('id') not in applied]
            for k, v in all_suggestions.items()
        }

class Organization(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

class OrganizationTemplate(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    docx_styles = models.JSONField(default=dict)  # Store styles as JSON
    is_default = models.BooleanField(default=False)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            AdminUser.objects.create(user=instance)
        
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1 and hasattr(instance, 'adminuser'):
        instance.adminuser.save()
    

