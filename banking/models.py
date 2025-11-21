from django.db import models
import uuid
import random
import string
from datetime import datetime
from django.core.exceptions import ValidationError

class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('savings', 'Savings'),
        ('checking', 'Checking'),
        ('business', 'Business'),
    )
    
    account_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_id')
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='savings')
    balance = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts'

    def __str__(self):
        return self.account_number

    def clean(self):
        if self.account_number and (len(self.account_number) != 10 or not self.account_number.isdigit()):
            raise ValidationError({
                'account_number': 'Account number must be exactly 10 digits.'
            })

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        
        # Ensure balance is float
        if not isinstance(self.balance, (int, float)):
            try:
                self.balance = float(self.balance)
            except (ValueError, TypeError):
                self.balance = 0.0
        
        self.balance = round(self.balance, 2)
        self.clean()
        super().save(*args, **kwargs)

    def generate_account_number(self):
        while True:
            account_num = ''.join(random.choices(string.digits, k=10))
            if not Account.objects.filter(account_number=account_num).exists():
                return account_num

    def get_formatted_account_number(self):
        if len(self.account_number) == 10:
            return f"{self.account_number[:4]}-{self.account_number[4:8]}-{self.account_number[8:]}"
        return self.account_number

    def update_balance(self, amount, operation='add'):
        # Ensure amount is float
        if not isinstance(amount, (int, float)):
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                amount = 0.0
        
        amount = round(amount, 2)
        
        if operation == 'add':
            self.balance += amount
        elif operation == 'subtract':
            self.balance -= amount
        else:
            raise ValueError("Operation must be 'add' or 'subtract'")
        
        # Round to 2 decimal places
        self.balance = round(self.balance, 2)
        self.save()
        return self.balance

    def can_withdraw(self, amount):
        # Ensure amount is float
        if not isinstance(amount, (int, float)):
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                amount = 0.0
        
        amount = round(amount, 2)
        return self.balance >= amount

    def get_formatted_balance(self):
        return f"${self.balance:.2f}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    )
    
    transaction_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, to_field='account_id')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.FloatField()
    description = models.CharField(max_length=200, blank=True)
    from_account = models.CharField(max_length=20, blank=True, null=True)
    to_account = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.type} - ${self.amount:.2f}"

    def save(self, *args, **kwargs):
        # Ensure amount is float
        if not isinstance(self.amount, (int, float)):
            try:
                self.amount = float(self.amount)
            except (ValueError, TypeError):
                self.amount = 0.0
        
        # Round to 2 decimal places
        self.amount = round(self.amount, 2)
        super().save(*args, **kwargs)

    def get_formatted_amount(self):
        return f"${self.amount:.2f}"

    def get_transaction_description(self):
        if self.type == 'transfer':
            if self.from_account:
                return f"Transfer to {self.to_account}"
            else:
                return f"Transfer from {self.from_account}"
        return self.description