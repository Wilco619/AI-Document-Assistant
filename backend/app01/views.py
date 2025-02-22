# app01/views.py

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document as DocxDocument

import string
import random
import logging

from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import now
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AdminUser, CustomUser, Document
from .nlp_processor import DocumentProcessor
from .models import ProcessedDocument, OrganizationTemplate
from .serializers import ProcessedDocumentSerializer, UserRegistrationSerializer


from .serializers import AdminUserSerializer, OTPSerializer, PasswordChangeSerializer, CustomUserSerializer, UserLoginSerializer

class UserRegistrationView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            # Create user with validated data
            user = CustomUser.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )

            # Generate OTP for email verification
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_generated_at = timezone.now()
            user.save()

            # Store user_id and OTP in session
            request.session['user_id'] = user.id
            request.session['otp'] = otp

            # Send verification email
            if settings.SEND_OTP_VIA_EMAIL:
                send_mail(
                    'Verify Your Email',
                    f'Your verification code is {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            else:
                print(f'Development mode: {user.email} verification code is {otp}')

            return Response({
                'message': 'Registration successful. Please verify your email.',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({
                'error': 'Registration failed',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            return Response({
                'error': 'Registration failed',
                'message': 'An unexpected error occurred during registration.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data

        if user is not None:
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_generated_at = timezone.now()
            user.save()

            request.session['user_id'] = user.id
            request.session['otp'] = otp

            if settings.SEND_OTP_VIA_EMAIL:
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            else:
                print(f'{user.email} Your OTP code is {otp}')

            return Response({
                'message': 'OTP generated. Check your email.',
                'user_id': user.id,
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

class VerifyOTPView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data.get('user_id')
            user = CustomUser.objects.get(id=user_id)

            # Generate JWT tokens
            token = RefreshToken.for_user(user)

            # Clear OTP fields after successful verification
            user.otp = None
            user.otp_generated_at = None
            user.save()

            return Response({
                'refresh': str(token),
                'access': str(token.access_token),
                'user_type': user.user_type
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class UserLogOutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logger.info(f"Received password change request for user: {request.user.username}")

        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            logger.info(f"Password successfully changed for user: {user.username}")
            return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Password change failed for user: {request.user.username}. Errors: {serializer.errors}")
            
            # Prepare a more user-friendly error message
            error_messages = []
            for field, errors in serializer.errors.items():
                for error in errors:
                    error_messages.append(str(error))
            
            return Response({
                "detail": "Password change failed",
                "errors": error_messages,
                "password_requirements": [
                    "Password must be at least 8 characters long",
                    "Password cannot be too similar to your username",
                    "Password must not be a commonly used password",
                    "Password must contain a mix of letters, numbers, and symbols"
                ]
            }, status=status.HTTP_400_BAD_REQUEST)


class UserInfoAPIView(RetrieveAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class=CustomUserSerializer

    def get_object(self):
        return self.request.user



CustomUser = get_user_model()
logger = logging.getLogger(__name__)

class CreateAdminUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def generate_random_password(self, length=8):
        characters = string.ascii_letters + string.digits  # Letters and digits only
        return ''.join(random.choice(characters) for _ in range(length))

    def send_password_email(self, email, username, password):
        subject = 'Your Admin Account Has Been Created'
        message = f'Hello {username},\n\nYour admin account has been created. Here are your login details:\n\nUsername: {email}\nPassword: {password}\n\nPlease change your password after your first login.\n\nBest regards,\nYour Application Team'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {str(e)}")

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Generate a random password if not provided
        password = request.data.get('password') or self.generate_random_password()

        custom_user_data = {
            'email': request.data.get('email'),
            'username': request.data.get('username') or request.data.get('email'),  # Use email as username if not provided
            'password': password,
            'user_type': 1,  # Ensure this user is an admi
        }

        try:
            # Validate custom user data
            for field in ['email', 'username']:
                if not custom_user_data[field]:
                    raise ValidationError(f"{field} is required")

            # Check if user already exists
            if CustomUser.objects.filter(email=custom_user_data['email']).exists():
                raise ValidationError("A user with this email already exists")

            # Use create_user method to ensure password hashing
            custom_user = CustomUser.objects.create_user(
                email=custom_user_data['email'],
                username=custom_user_data['username'],
                password=password,  # Use the generated or provided password
                user_type=custom_user_data['user_type'],
            )

            admin_user, created = AdminUser.objects.get_or_create(user=custom_user)
            if not created:
                admin_user.save()

            # Send email with login credentials
            self.send_password_email(custom_user.email, custom_user.username, password)

            response_data = {
                'custom_user': CustomUserSerializer(custom_user).data,
                'admin_user': AdminUserSerializer(admin_user).data,
                'message': 'Admin user created successfully. Login credentials have been sent to the provided email.'
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}", exc_info=True)
            return Response({'detail': 'An error occurred while creating the admin user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes=(IsAuthenticated,)  # Adjust as needed

class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes=(IsAuthenticated,)
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer
    # permission_classes = [permissions.IsAdminUser]  # Admin-only access

# Updated Django view that integrates with the DocumentProcessor
def process_uploaded_document(uploaded_file):
    """Process an uploaded document and return data ready for model storage"""
    processor = DocumentProcessor()
    
    # Process the document
    try:
        start_time = datetime.now()  # Capture start time
        result = processor.process_file(uploaded_file)  # Process file
        end_time = datetime.now()  # Capture end time

        processing_time = end_time - start_time 
        
        # Prepare result for model
        return {
            'original_text': result['original_text'],
            'improved_text': result['improved_text'],
            'grammar_suggestions': result['grammar_suggestions'],
            'style_suggestions': result['style_suggestions'],
            'clarity_improvements': result['clarity_improvements'],
            'tone_analysis': result['tone_analysis'],
            'consistency_score': result['consistency_score'],
            'document_stats': result['document_stats'],
            'processing_time': processing_time
        }
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

# Updated ViewSet create method
class ProcessedDocumentViewSet(viewsets.ModelViewSet):
    queryset = ProcessedDocument.objects.all()
    serializer_class = ProcessedDocumentSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def create(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type
        allowed_extensions = [".txt", ".pdf", ".docx"]
        if not any(uploaded_file.name.endswith(ext) for ext in allowed_extensions):
            return Response({"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Process document
            result = process_uploaded_document(uploaded_file)
            
            # Create the processed document record
            processed_doc = ProcessedDocument.objects.create(
                user=request.user,
                original_text=result['original_text'],
                improved_text=result['improved_text'],
                grammar_suggestions=result['grammar_suggestions'],
                style_suggestions=result['style_suggestions'],
                clarity_improvements=result['clarity_improvements'],
                tone_analysis=result['tone_analysis'],
                consistency_score=result['consistency_score'],
                document_stats=result['document_stats'],
                processing_time=now(),
                status='processed'
            )
            
            serializer = self.get_serializer(processed_doc)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Processing failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def apply_suggestion(self, request, pk=None):
        processed_doc = self.get_object()
        suggestion = request.data.get('suggestion')
        action = request.data.get('action')

        if action == 'accept':
            # Apply the suggestion to the improved text
            improved_text = processed_doc.improved_text
            if suggestion.get('original') and suggestion.get('suggested'):
                improved_text = improved_text.replace(
                    suggestion['original'],
                    suggestion['suggested']
                )
            
            processed_doc.improved_text = improved_text
            processed_doc.applied_suggestions = (
                processed_doc.applied_suggestions or []
            ) + [suggestion]
            processed_doc.save()

        serializer = self.get_serializer(processed_doc)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def export(self, request, pk=None):
        """Export the processed document as TXT, PDF, or DOCX"""
        try:
            document = ProcessedDocument.objects.get(id=pk)
        except ProcessedDocument.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

        export_format = request.query_params.get("format", "txt")  # Default format is TXT

        if export_format == "txt":
            response = HttpResponse(document.improved_text, content_type="text/plain")
            response["Content-Disposition"] = f'attachment; filename="document_{pk}.txt"'
        
        elif export_format == "pdf":
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, document.improved_text[:1000])  # Adjust for PDF layout
            p.showPage()
            p.save()
            buffer.seek(0)

            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="document_{pk}.pdf"'
        
        elif export_format == "docx":
            doc = DocxDocument()
            doc.add_paragraph(document.improved_text)
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            response = HttpResponse(
                buffer,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="document_{pk}.docx"'
        
        else:
            return Response({"error": "Invalid format"}, status=400)

        return response