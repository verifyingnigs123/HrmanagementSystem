from rest_framework import serializers
from .models import Employee, Attendance
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'user', 'role', 'employee_id', 'department', 'position', 'phone', 'hire_date']

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'status', 'check_in_time', 'check_out_time', 'notes']
        read_only_fields = ['id', 'created_at']

class AttendanceCheckInSerializer(serializers.Serializer):
    """For mobile check-in with GPS (GPS is optional)"""
    check_in_time = serializers.TimeField(required=False)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self):
        latitude = self.initial_data.get('latitude')
        longitude = self.initial_data.get('longitude')
        
        # Only validate if both are provided
        if latitude is not None and longitude is not None:
            if not (-90 <= latitude <= 90):
                raise serializers.ValidationError("Invalid latitude")
            if not (-180 <= longitude <= 180):
                raise serializers.ValidationError("Invalid longitude")
        return self.initial_data

class AttendanceCheckOutSerializer(serializers.Serializer):
    """For mobile check-out with GPS (GPS is optional)"""
    check_out_time = serializers.TimeField(required=False)
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
