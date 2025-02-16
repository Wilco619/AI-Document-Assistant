from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    # Fix the clash by setting a unique related_name
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True
    )

    class Meta:
        db_table = 'users'

class Document(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed')
    ]
    
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    temp_user_id = models.CharField(max_length=36, null=True, blank=True)  # Store temporary ID
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        
class DocumentContent(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    original_content = models.TextField()
    improved_content = models.TextField(null=True, blank=True)
    tone_analysis = models.JSONField(null=True, blank=True)
    consistency_score = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'document_content'

class Suggestion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    subtype = models.CharField(max_length=50, blank=True)
    original_text = models.TextField()
    suggestion = models.TextField()
    position_start = models.IntegerField()
    position_end = models.IntegerField()
    confidence = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('applied', 'Applied'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'suggestions'
        ordering = ['-confidence', 'created_at']

class DocumentStatistics(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    num_sentences = models.IntegerField()
    num_words = models.IntegerField()
    num_paragraphs = models.IntegerField()
    avg_sentence_length = models.FloatField()
    readability_score = models.FloatField()
    vocabulary_diversity = models.FloatField()
    tone_confidence = models.FloatField(null=True)
    consistency_details = models.JSONField(null=True)
    
    class Meta:
        db_table = 'document_statistics'

