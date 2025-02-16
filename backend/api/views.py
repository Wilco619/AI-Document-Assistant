# views.py
import uuid
from requests import request
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Document, DocumentContent, Suggestion, DocumentStatistics
from .serializers import (
    UserProfileSerializer, UserSerializer, UserRegistrationSerializer, 
    DocumentSerializer, DocumentContentSerializer,
    SuggestionSerializer, DocumentStatisticsSerializer
)
from .nlp_processor import DocumentProcessor
from .utils import DocumentConverter
import logging

from api import models

logger = logging.getLogger(__name__)
User = get_user_model()

class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create auth token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                return Response(
                    {'error': 'Please verify your email'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Migrate temporary documents to the logged-in user
            temp_user_id = request.session.get('temp_user_id')
            if temp_user_id:
                Document.objects.filter(temp_user_id=temp_user_id, user__isnull=True).update(user=user, temp_user_id=None)
                del request.session['temp_user_id']  # Clear the session ID

            # ✅ Issue authentication token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        token = request.data.get('token')
        user = get_object_or_404(User, email_verification_token=token)
        user.is_verified = True
        user.save()
        return Response({'message': 'Email verified successfully'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'})
    
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_temporary_user_id(self):
        """Generate or retrieve a temporary user ID for anonymous users using sessions."""
        if not self.request.user.is_authenticated:
            if 'temp_user_id' not in self.request.session:
                self.request.session['temp_user_id'] = str(uuid.uuid4())  # Generate and store in session
            return self.request.session['temp_user_id']
        return None

    def get_queryset(self):
        user = self.request.user
        temp_user_id = self.get_temporary_user_id()  # Use instance method

        if user.is_authenticated:
            return Document.objects.filter(user=user).prefetch_related(
                'documentcontent',
                'documentstatistics',
                'suggestion_set'
            )
        else:
            return Document.objects.filter(temp_user_id=temp_user_id)

    def create(self, request):
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        document = None
        
        try:
            # Handle anonymous users by assigning a temporary ID
            if request.user.is_authenticated:
                user = request.user
                temp_user_id = None
            else:
                user = None
                temp_user_id = self.get_temporary_user_id()  # Retrieve temp ID

            # Create document
            document = Document.objects.create(
                user=user,  # None for anonymous users
                temp_user_id=temp_user_id,  # Store temporary user ID
                title=file.name,
                file=file,
                file_type=file.name.split('.')[-1].lower(),
                status='processing'
            )

            # Store the document ID in session for anonymous users to track later
            if user is None:
                if 'anonymous_documents' not in request.session:
                    request.session['anonymous_documents'] = []
                request.session['anonymous_documents'].append(document.id)
                request.session.modified = True  # Ensure session changes are saved

            # Extract and process content
            processor = DocumentProcessor()
            content, _ = DocumentConverter.extract_text(file)
            
            # Create document content
            doc_content = DocumentContent.objects.create(
                document=document,
                original_content=content
            )
            
            # Process document
            results = processor.process_document(content)
            
            # Create suggestions
            suggestions = []
            for category in ['grammar_suggestions', 'style_suggestions', 'clarity_improvements']:
                if category in results:
                    for sugg in results[category]:
                        suggestions.append(Suggestion(
                            document=document,
                            type=category.split('_')[0],
                            subtype=sugg.get('subtype', ''),
                            original_text=sugg['original'],
                            suggestion=sugg['suggestion'],
                            position_start=sugg['position']['start'],
                            position_end=sugg['position']['end'],
                            confidence=sugg.get('confidence', 0.5)
                        ))
            
            Suggestion.objects.bulk_create(suggestions)
            
            # Update document content with analysis results
            doc_content.improved_content = content  # Initial content, will be updated with suggestions
            doc_content.tone_analysis = results.get('tone_analysis')
            doc_content.consistency_score = results.get('consistency_score')
            doc_content.save()
            
            # Create document statistics
            DocumentStatistics.objects.create(
                document=document,
                **results['document_stats']
            )
            
            # Update document status
            document.status = 'processed'
            document.save()
            
            return Response(
                self.get_serializer(document).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            if document:
                document.status = 'failed'
                document.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


    
    @action(detail=True, methods=['post'])
    def apply_suggestion(self, request, pk=None):
        document = self.get_object()
        suggestion_id = request.data.get('suggestion_id')
        
        if not suggestion_id:
            return Response(
                {'error': 'suggestion_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        suggestion = get_object_or_404(
            Suggestion,
            id=suggestion_id,
            document=document
        )
        
        try:
            content = document.documentcontent
            current_text = content.improved_content or content.original_content
            
            # Apply the suggestion to the content
            before = current_text[:suggestion.position_start]
            after = current_text[suggestion.position_end:]
            new_content = before + suggestion.suggestion + after
            
            # Update the content
            content.improved_content = new_content
            content.save()
            
            # Update suggestion status
            suggestion.status = 'applied'
            suggestion.save()
            
            return Response(self.get_serializer(document).data)
            
        except Exception as e:
            logger.error(f"Error applying suggestion: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject_suggestion(self, request, pk=None):
        document = self.get_object()
        suggestion_id = request.data.get('suggestion_id')
        
        suggestion = get_object_or_404(
            Suggestion,
            id=suggestion_id,
            document=document
        )
        
        suggestion.status = 'rejected'
        suggestion.save()
        
        return Response(self.get_serializer(document).data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        document = self.get_object()
        statistics = document.documentstatistics
        return Response(DocumentStatisticsSerializer(statistics).data)
    
    @action(detail=True, methods=['get'])
    def suggestions(self, request, pk=None):
        document = self.get_object()
        suggestions = document.suggestion_set.all()
        
        # Filter by type if requested
        suggestion_type = request.query_params.get('type')
        if suggestion_type:
            suggestions = suggestions.filter(type=suggestion_type)
        
        # Filter by status if requested
        status = request.query_params.get('status')
        if status:
            suggestions = suggestions.filter(status=status)
        
        return Response(SuggestionSerializer(suggestions, many=True).data)
    
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        document = self.get_object()
        content = document.documentcontent
        return Response(DocumentContentSerializer(content).data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for user's documents"""
        stats = Document.objects.filter(user=request.user).aggregate(
            total_documents=Count('id'),
            processed_documents=Count('id', filter=models.Q(status='processed')),
            failed_documents=Count('id', filter=models.Q(status='failed'))
        )
        
        # Get counts by document type
        file_types = Document.objects.filter(user=request.user)\
            .values('file_type')\
            .annotate(count=Count('id'))
        
        stats['file_types'] = {
            item['file_type']: item['count'] 
            for item in file_types
        }
        
        return Response(stats)

class SuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SuggestionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return Suggestion.objects.filter(
            document__user=self.request.user
        ).select_related('document')
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        suggestion = self.get_object()
        document = suggestion.document
        
        try:
            content = document.documentcontent
            current_text = content.improved_content or content.original_content
            
            # Apply the suggestion
            before = current_text[:suggestion.position_start]
            after = current_text[suggestion.position_end:]
            new_content = before + suggestion.suggestion + after
            
            content.improved_content = new_content
            content.save()
            
            suggestion.status = 'applied'
            suggestion.save()
            
            return Response(self.get_serializer(suggestion).data)
            
        except Exception as e:
            logger.error(f"Error applying suggestion: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        return self.request.user
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)