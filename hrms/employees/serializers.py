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
    """For mobile check-in with GPS"""
    check_in_time = serializers.TimeField(required=False)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate(self):
        if not (-90 <= self.initial_data.get('latitude', 0) <= 90):
            raise serializers.ValidationError("Invalid latitude")
        if not (-180 <= self.initial_data.get('longitude', 0) <= 180):
            raise serializers.ValidationError("Invalid longitude")
        return self.initial_data

class AttendanceCheckOutSerializer(serializers.Serializer):
    """For mobile check-out with GPS"""
    check_out_time = serializers.TimeField(required=False)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
