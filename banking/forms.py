from django import forms
from django.core.validators import MinValueValidator

class UserRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter email address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter password'
        })
    )
    confirm_password = forms.CharField(  # Make sure this field exists
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirm password'
        })
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter last name'
        })
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter phone number'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your password'
        })
    )

class TransactionForm(forms.Form):
    amount = forms.FloatField(
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01'
        })
    )
    description = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter description (optional)'
        })
    )
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0.00:
            raise forms.ValidationError("Amount must be greater than zero.")
        
        # Round to 2 decimal places
        return round(amount, 2)

class TransferForm(forms.Form):
    to_account = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control account-input',
            'placeholder': 'Enter recipient account number (10 digits)',
            'pattern': '[0-9]{10}',
            'title': 'Please enter exactly 10-digit account number'
        })
    )
    amount = forms.FloatField(
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01'
        })
    )
    description = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter description (optional)'
        })
    )
    
    def clean_to_account(self):
        to_account = self.cleaned_data['to_account']
        if len(to_account) != 10 or not to_account.isdigit():
            raise forms.ValidationError("Account number must be exactly 10 digits.")
        return to_account
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0.00:
            raise forms.ValidationError("Amount must be greater than zero.")
        
        # Round to 2 decimal places
        return round(amount, 2)