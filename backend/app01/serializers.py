# serializers.py

from django.forms import ValidationError
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, AdminUser, ProcessedDocument

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match."
            })

        # Validate password strength
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })

        # Remove password_confirm from the data
        if 'password_confirm' in data:
            data.pop('password_confirm')

        return data

    def validate_email(self, value):
        # Check if email already exists
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        # Check if username already exists
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.CharField()
    password=serializers.CharField(write_only=True)

    class Meta:
        model=CustomUser
        fields=["email","password"]


    def validate(self, data):
        user=authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class OTPSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    otp = serializers.CharField()

    def validate(self, data):
        user_id = data.get('user_id')
        otp = data.get('otp')

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")

        # Check if OTP is expired
        if user.otp_generated_at and (timezone.now() - user.otp_generated_at) > timedelta(hours=2):
            raise serializers.ValidationError("OTP has expired")

        # Check if OTP is correct
        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP")

        return data
    

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value

    def validate_new_password(self, value):
        user = self.context['request'].user
        try:
            validate_password(value, user)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        username = validated_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError({"username": "This username is already taken."})

        user = CustomUser.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
        )
        return user
    
    def update(self, instance, validated_data):
        # Handle updates here if needed
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        
        # Password update should be handled separately
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance
    
class AdminUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    username = serializers.CharField(write_only=True)

    class Meta:
        model = AdminUser
        fields = [
            'id',
            'email',
            'username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        email = validated_data.pop('email')
        username = validated_data.pop('username')
       

        user = CustomUser.objects.create_user(
            email=email,
            username=username,
            password=validated_data.pop('password', ''), 
            user_type=1,  # AdminUser
        )

        admin_user = AdminUser.objects.create(
            user=user,
        )

        return admin_user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['email'] = instance.user.email
        representation['username'] = instance.user.username
        return representation

class ProcessedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedDocument
        fields = '__all__'

        
#Dashboard
class DashboardSerializer(serializers.Serializer):
    total_customers = serializers.IntegerField()
    active_loans = serializers.IntegerField()
    total_staff = serializers.IntegerField()
    branches = serializers.ListField(child=serializers.DictField())
    recent_customers = serializers.ListField(child=serializers.DictField())
    loan_distribution = serializers.ListField(child=serializers.DictField())
    monthly_loans = serializers.ListField(child=serializers.DictField())
    collection_rate = serializers.FloatField()
    customer_satisfaction = serializers.FloatField()
    cumulative_collection_rate = serializers.FloatField()
    arrears_collected = serializers.FloatField()
    customer_growth = serializers.ListField(child=serializers.DictField())
    loan_growth = serializers.ListField(child=serializers.DictField())
    staff_growth = serializers.ListField(child=serializers.DictField())
    branch_growth = serializers.ListField(child=serializers.DictField())
