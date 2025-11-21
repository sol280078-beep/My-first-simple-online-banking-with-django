from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Account, Transaction
from .forms import UserRegistrationForm, LoginForm, TransactionForm, TransferForm
# import uuid
from django.db import transaction as db_transaction
from django.db.models import Sum

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return render(request, 'banking/register.html', {'form': form})
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email address already registered. Please use a different email.')
                return render(request, 'banking/register.html', {'form': form})
            
            user = User(
                username=username,
                email=email,
                password=make_password(password),
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone']
            )
            user.save()
            
            account = Account(user=user, account_type='savings')
            account.save()
            
            messages.success(request, f'Registration successful! Your account has been created. Your account number is {account.account_number}')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'banking/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    request.session['user_id'] = user.user_id
                    request.session['username'] = user.username
                    request.session['user_full_name'] = user.get_full_name()
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid password. Please try again.')
            except User.DoesNotExist:
                messages.error(request, 'User does not exist. Please check your username or register for a new account.')
    else:
        form = LoginForm()
    
    return render(request, 'banking/login.html', {'form': form})

def user_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def dashboard(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to access your dashboard.')
        return redirect('login')
    
    user_id = request.session['user_id']
    try:
        user = User.objects.get(user_id=user_id)
        accounts = Account.objects.filter(user=user)
        
        context = {
            'user': user,
            'accounts': accounts
        }
        return render(request, 'banking/dashboard.html', context)
    except User.DoesNotExist:
        messages.error(request, 'User account not found. Please log in again.')
        return redirect('login')

def deposit(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to perform transactions.')
        return redirect('login')
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            user_id = request.session['user_id']
            try:
                user = User.objects.get(user_id=user_id)
                account = Account.objects.get(user=user)
                amount = form.cleaned_data['amount']
                description = form.cleaned_data.get('description', 'Deposit')
                
                old_balance = account.balance
                account.update_balance(amount, 'add')
                new_balance = account.balance
                
                transaction = Transaction(
                    account=account,
                    type='deposit',
                    amount=amount,
                    description=description
                )
                transaction.save()
                
                messages.success(request, f'Successfully deposited ${amount:.2f}. Your new balance is ${new_balance:.2f}')
                return redirect('dashboard')
                
            except (User.DoesNotExist, Account.DoesNotExist):
                messages.error(request, 'Account not found. Please contact support.')
                return redirect('dashboard')
    else:
        form = TransactionForm()
    
    return render(request, 'banking/transaction.html', {
        'form': form, 
        'transaction_type': 'Deposit',
        'title': 'Make a Deposit'
    })

def withdraw(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to perform transactions.')
        return redirect('login')
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            user_id = request.session['user_id']
            try:
                user = User.objects.get(user_id=user_id)
                account = Account.objects.get(user=user)
                amount = form.cleaned_data['amount']
                description = form.cleaned_data.get('description', 'Withdrawal')
                
                if account.can_withdraw(amount):
                    old_balance = account.balance
                    account.update_balance(amount, 'subtract')
                    new_balance = account.balance
                    
                    transaction = Transaction(
                        account=account,
                        type='withdrawal',
                        amount=amount,
                        description=description
                    )
                    transaction.save()
                    
                    messages.success(request, f'Successfully withdrew ${amount:.2f}. Your new balance is ${new_balance:.2f}')
                    return redirect('dashboard')
                else:
                    messages.error(request, f'Insufficient funds. Your current balance is ${account.balance:.2f}')
                    
            except (User.DoesNotExist, Account.DoesNotExist):
                messages.error(request, 'Account not found. Please contact support.')
                return redirect('dashboard')
    else:
        form = TransactionForm()
    
    return render(request, 'banking/transaction.html', {
        'form': form, 
        'transaction_type': 'Withdraw',
        'title': 'Make a Withdrawal'
    })

def transfer(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to perform transactions.')
        return redirect('login')
    
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            user_id = request.session['user_id']
            to_account_number = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', 'Transfer')
            
            try:
                user = User.objects.get(user_id=user_id)
                from_account = Account.objects.get(user=user)
                
                if from_account.account_number == to_account_number:
                    messages.error(request, 'Cannot transfer to your own account. Please enter a different account number.')
                    return render(request, 'banking/transfer.html', {'form': form})
                
                try:
                    to_account = Account.objects.get(account_number=to_account_number)
                    
                    if from_account.can_withdraw(amount):
                        with db_transaction.atomic():
                            from_old_balance = from_account.balance
                            from_account.update_balance(amount, 'subtract')
                            from_new_balance = from_account.balance
                            
                            to_old_balance = to_account.balance
                            to_account.update_balance(amount, 'add')
                            to_new_balance = to_account.balance
                            
                            Transaction.objects.create(
                                account=from_account,
                                type='transfer',
                                amount=amount,
                                description=f"Transfer to {to_account_number}: {description}",
                                to_account=to_account_number
                            )
                            
                            Transaction.objects.create(
                                account=to_account,
                                type='transfer',
                                amount=amount,
                                description=f"Transfer from {from_account.account_number}: {description}",
                                from_account=from_account.account_number
                            )
                        
                        messages.success(request, f'Successfully transferred ${amount:.2f} to account {to_account_number}. Your new balance is ${from_new_balance:.2f}')
                        return redirect('dashboard')
                    else:
                        messages.error(request, f'Insufficient funds. Your current balance is ${from_account.balance:.2f}')
                        
                except Account.DoesNotExist:
                    messages.error(request, f'Recipient account {to_account_number} not found. Please check the account number and try again.')
                    
            except (User.DoesNotExist, Account.DoesNotExist):
                messages.error(request, 'Your account was not found. Please contact support.')
                return redirect('dashboard')
    else:
        form = TransferForm()
    
    return render(request, 'banking/transfer.html', {'form': form})

def transaction_history(request):
    if 'user_id' not in request.session:
        messages.error(request, 'Please log in to view transaction history.')
        return redirect('login')
    
    user_id = request.session['user_id']
    try:
        user = User.objects.get(user_id=user_id)
        account = Account.objects.get(user=user)
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')[:50]
        
        total_deposits = Transaction.objects.filter(
            account=account, 
            type='deposit'
        ).aggregate(total=Sum('amount'))['total'] or 0.00
        
        total_withdrawals = Transaction.objects.filter(
            account=account, 
            type='withdrawal'
        ).aggregate(total=Sum('amount'))['total'] or 0.00
        
        total_transfers_out = Transaction.objects.filter(
            account=account, 
            type='transfer',
            from_account=account.account_number
        ).aggregate(total=Sum('amount'))['total'] or 0.00
        
        context = {
            'transactions': transactions,
            'account': account,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_transfers_out': total_transfers_out,
        }
        return render(request, 'banking/transaction_history.html', context)
        
    except (User.DoesNotExist, Account.DoesNotExist):
        messages.error(request, 'Account not found. Please contact support.')
        return redirect('dashboard')  