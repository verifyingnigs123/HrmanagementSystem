from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime
import json

from .models import Employee, Attendance
from .serializers import (
    EmployeeSerializer,
    AttendanceSerializer,
    AttendanceCheckInSerializer,
    AttendanceCheckOutSerializer,
)

# ============ AUTHENTICATION ENDPOINTS ============

@api_view(['POST'])
def mobile_login(request):
    """Mobile app login endpoint"""
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user is not None:
        try:
            employee = Employee.objects.get(user=user)
            # In production, use token authentication (Django REST Token)
            return Response({
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'employee_id': employee.employee_id,
                'role': employee.role,
                'department': employee.department,
            }, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Employee profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(
        {'success': False, 'message': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


# ============ ATTENDANCE ENDPOINTS ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_today_attendance(request):
    """Get today's attendance status for the current user"""
    try:
        employee = Employee.objects.get(user=request.user)
        today = timezone.now().date()
        
        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if attendance:
            serializer = AttendanceSerializer(attendance)
            return Response({
                'success': True,
                'data': serializer.data,
                'checked_in': attendance.check_in_time is not None,
                'checked_out': attendance.check_out_time is not None,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': True,
                'data': None,
                'checked_in': False,
                'checked_out': False,
                'message': 'No attendance record for today',
            }, status=status.HTTP_200_OK)
            
    except Employee.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_in(request):
    """Mobile check-in endpoint with GPS"""
    try:
        employee = Employee.objects.get(user=request.user)
        today = timezone.now().date()
        
        # Get or create attendance record for today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'status': 'present'}
        )
        
        if attendance.check_in_time is not None:
            return Response({
                'success': False,
                'message': 'Already checked in today at ' + str(attendance.check_in_time),
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate GPS coordinates
        serializer = AttendanceCheckInSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update attendance record
        attendance.check_in_time = timezone.now().time()
        attendance.status = 'present'
        
        # Store GPS data if provided (you can extend the Attendance model for this)
        if request.data.get('notes'):
            attendance.notes = f"GPS: {request.data.get('latitude')}, {request.data.get('longitude')} - {request.data.get('notes')}"
        else:
            attendance.notes = f"GPS: {request.data.get('latitude')}, {request.data.get('longitude')}"
        
        attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response({
            'success': True,
            'message': 'Checked in successfully',
            'data': serializer.data,
        }, status=status.HTTP_201_CREATED)
        
    except Employee.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_out(request):
    """Mobile check-out endpoint with GPS"""
    try:
        employee = Employee.objects.get(user=request.user)
        today = timezone.now().date()
        
        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if not attendance:
            return Response({
                'success': False,
                'message': 'No check-in record found for today. Please check in first.',
            }, status=status.HTTP_404_NOT_FOUND)
        
        if attendance.check_out_time is not None:
            return Response({
                'success': False,
                'message': 'Already checked out today at ' + str(attendance.check_out_time),
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate GPS coordinates
        serializer = AttendanceCheckOutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update attendance record
        attendance.check_out_time = timezone.now().time()
        
        # Append GPS data to notes
        gps_note = f"Check-out GPS: {request.data.get('latitude')}, {request.data.get('longitude')}"
        if request.data.get('notes'):
            gps_note += f" - {request.data.get('notes')}"
        
        if attendance.notes:
            attendance.notes += f"\n{gps_note}"
        else:
            attendance.notes = gps_note
        
        attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response({
            'success': True,
            'message': 'Checked out successfully',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
        
    except Employee.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attendance_history(request):
    """Get attendance history for the current user (last 30 days)"""
    try:
        employee = Employee.objects.get(user=request.user)
        
        # Get last 30 days
        from datetime import timedelta
        start_date = timezone.now().date() - timedelta(days=30)
        
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__gte=start_date
        ).order_by('-date')
        
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response({
            'success': True,
            'count': attendance_records.count(),
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
        
    except Employee.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_profile(request):
    """Get current employee profile"""
    try:
        employee = Employee.objects.get(user=request.user)
        serializer = EmployeeSerializer(employee)
        return Response({
            'success': True,
            'data': serializer.data,
        }, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Employee not found'},
            status=status.HTTP_404_NOT_FOUND
        )
