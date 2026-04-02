from django import forms
from django.contrib.auth.models import User
from .models import Employee
import uuid

class UserCreationForm(forms.Form):
    """Form for creating a new user with employee details."""
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    role = forms.ChoiceField(
        choices=[
            ('employee', 'Employee'),
            ('manager', 'Manager'),
            ('hradmin', 'HR Admin'),
            ('admin', 'Administrator'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    department = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department'
        })
    )
    position = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Position'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    hire_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean_username(self):
        """Check if username already exists."""
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        """Check if email already exists."""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def save(self):
        """Create a new User and Employee."""
        try:
            # Create Django User
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
            )

            # Create Employee record
            employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
            employee = Employee.objects.create(
                user=user,
                employee_id=employee_id,
                role=self.cleaned_data['role'],
                department=self.cleaned_data['department'],
                position=self.cleaned_data['position'],
                phone=self.cleaned_data['phone'],
                hire_date=self.cleaned_data['hire_date'],
            )

            return employee
        except Exception as e:
            raise forms.ValidationError(f"Error creating user: {str(e)}")


class UserUpdateForm(forms.Form):
    """Form for updating user details."""
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    role = forms.ChoiceField(
        choices=[
            ('employee', 'Employee'),
            ('manager', 'Manager'),
            ('hradmin', 'HR Admin'),
            ('admin', 'Administrator'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    department = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department'
        })
    )
    position = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Position'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def save(self, user, employee):
        """Update existing User and Employee."""
        try:
            # Update User
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()

            # Update Employee
            employee.role = self.cleaned_data['role']
            employee.department = self.cleaned_data['department']
            employee.position = self.cleaned_data['position']
            employee.phone = self.cleaned_data['phone']
            employee.is_active = self.cleaned_data['is_active']
            employee.save()

            return employee
        except Exception as e:
            raise forms.ValidationError(f"Error updating user: {str(e)}")
