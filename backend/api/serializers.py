from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Document, DocumentContent, Suggestion, DocumentStatistics

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_verified', 'created_at')
        read_only_fields = ('is_verified', 'created_at')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class DocumentContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentContent
        fields = ('original_content', 'improved_content', 'tone_analysis', 'consistency_score')

class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = '__all__'

class DocumentStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentStatistics
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    content = DocumentContentSerializer(source='documentcontent', read_only=True)
    statistics = DocumentStatisticsSerializer(source='documentstatistics', read_only=True)
    suggestions = SuggestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ('id', 'title', 'file', 'file_type', 'status', 'created_at', 
                 'content', 'statistics', 'suggestions')
        read_only_fields = ('status', 'created_at')

class UserProfileSerializer(serializers.ModelSerializer):
    total_documents = serializers.SerializerMethodField()
    processed_documents = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'created_at', 
                 'is_verified', 'total_documents', 'processed_documents')
        read_only_fields = ('email', 'created_at', 'is_verified')
    
    def get_total_documents(self, obj):
        return Document.objects.filter(user=obj).count()
    
    def get_processed_documents(self, obj):
        return Document.objects.filter(user=obj, status='processed').count()
