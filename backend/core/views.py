from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.http import HttpResponse
from .models import UploadHistory, EquipmentData
from .serializers import UploadHistorySerializer, EquipmentDataSerializer, UserSerializer, RegisterSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail # Kept for potential future use, but we will print to console
from django.conf import settings

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"http://localhost:5173/reset-password/{uid}/{token}" # Assuming frontend runs on 5173
                
                # Print to console for development
                print(f"\n[PASSWORD RESET] Link for {email}: {reset_link}\n")
                
                return Response({"message": "Password reset link has been sent to your email (check console)."}, status=status.HTTP_200_OK)
            return Response({"error": "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid token or user ID."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(f"DEBUG: FileUploadView called. User: {request.user}, IsAuth: {request.user.is_authenticated}")
        # print(f"DEBUG: Data: {request.data}") 
        
        file_serializer = UploadHistorySerializer(data=request.data)
        if file_serializer.is_valid():
            # Save with user if authenticated
            if request.user.is_authenticated:
                upload_instance = file_serializer.save(user=request.user)
            else:
                # This branch should not be reached if IsAuthenticated is set, but keeping as fallback
                print("DEBUG: User not authenticated, saving without user.")
                upload_instance = file_serializer.save()
            
            try:
                # Process CSV
                df = pd.read_csv(upload_instance.file.path)
                
                # Cleanup column names
                df.columns = [c.strip() for c in df.columns]
                
                equipment_list = []
                for _, row in df.iterrows():
                    equipment_list.append(EquipmentData(
                        upload=upload_instance,
                        equipment_name=row['Equipment Name'],
                        equipment_type=row['Type'],
                        flowrate=row['Flowrate'],
                        pressure=row['Pressure'],
                        temperature=row['Temperature']
                    ))
                
                EquipmentData.objects.bulk_create(equipment_list)
                
                upload_instance.total_records = len(equipment_list)
                upload_instance.save()
                
                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                upload_instance.delete()
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, upload_id, *args, **kwargs):
        try:
            # Ensure upload belongs to the user
            upload_instance = UploadHistory.objects.get(id=upload_id, user=request.user)
            equipment = EquipmentData.objects.filter(upload=upload_instance)
            
            # Aggregation
            aggregates = equipment.aggregate(
                avg_flowrate=Avg('flowrate'),
                avg_pressure=Avg('pressure'),
                avg_temperature=Avg('temperature')
            )
            
            # Type Distribution
            type_distribution = equipment.values('equipment_type').annotate(count=Count('id'))
            
            return Response({
                "upload_id": upload_id,
                "total_count": equipment.count(),
                "averages": aggregates,
                "type_distribution": type_distribution
            }, status=status.HTTP_200_OK)
        except UploadHistory.DoesNotExist:
            return Response({"error": "Upload not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        history = UploadHistory.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
        serializer = UploadHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EquipmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, upload_id):
        # Ensure upload belongs to user implicitly by checking if upload exists for user
        if not UploadHistory.objects.filter(id=upload_id, user=request.user).exists():
             return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
             
        equipment = EquipmentData.objects.filter(upload_id=upload_id)
        serializer = EquipmentDataSerializer(equipment, many=True)
        return Response(serializer.data)

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class PDFReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, upload_id):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{upload_id}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0f172a'),
            alignment=1,
            spaceAfter=20
        )
        elements.append(Paragraph("Chemical Equipment Report", title_style))
        elements.append(Spacer(1, 10))

        # Metadata
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray
        )
        elements.append(Paragraph(
            f"<b>Upload ID:</b> {upload_id} | <b>User:</b> {request.user.username} | <b>Date:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
            meta_style))
        elements.append(Spacer(1, 20))

        try:
            upload = UploadHistory.objects.get(id=upload_id, user=request.user)
            equipment = EquipmentData.objects.filter(upload=upload)

            # Aggregates
            aggregates = equipment.aggregate(
                avg_flow=Avg('flowrate'),
                avg_press=Avg('pressure'),
                avg_temp=Avg('temperature')
            )

            # Summary Table
            summary_data = [
                ['Metric', 'Value'],
                ['Total Records', str(equipment.count())],
                ['Average Flowrate', f"{aggregates['avg_flow']:.2f}" if aggregates['avg_flow'] else "0"],
                ['Average Pressure', f"{aggregates['avg_press']:.2f}" if aggregates['avg_press'] else "0"],
                ['Average Temperature', f"{aggregates['avg_temp']:.2f}" if aggregates['avg_temp'] else "0"]
            ]

            summary_table = Table(summary_data, colWidths=[250, 200])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0ea5e9')),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f9ff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bae6fd')),
            ]))

            elements.append(Paragraph("Summary Statistics", styles['Heading2']))
            elements.append(summary_table)
            elements.append(Spacer(1, 25))

            # Equipment Table
            elements.append(Paragraph("Equipment Details (Top 50)", styles['Heading2']))

            data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
            for item in equipment[:50]:
                data.append([
                    item.equipment_name,
                    item.equipment_type,
                    str(item.flowrate),
                    str(item.pressure),
                    str(item.temperature)
                ])

            data_table = Table(data, colWidths=[140, 120, 80, 80, 80])
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            elements.append(data_table)

        except UploadHistory.DoesNotExist:
            elements.append(Paragraph("Upload not found or access denied.", styles['Normal']))

        doc.build(elements)
        return response
