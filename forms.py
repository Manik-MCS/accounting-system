from django import forms
from .models import Member, Project, Recipient, Investment, Deposit, Payment, Profit
from datetime import datetime

class RecipientForm(forms.ModelForm):
    """যাকে টাকা দেওয়া হবে (Recipient) তাকে অ্যাড করার ফর্ম"""
    class Meta:
        model = Recipient
        fields = ['name', 'phone', 'nid', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'গ্রহীতার নাম'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ফোন নম্বর'}),
            'nid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NID নম্বর'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ঠিকানা'}),
        }


class MemberForm(forms.ModelForm):
    """Form for adding/editing members"""
    class Meta:
        model = Member
        fields = ['member_id', 'name', 'phone', 'email', 'address', 'profit_share_percentage']
        widgets = {
            'member_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 162501'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Member Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '01XXXXXXXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Full Address'
            }),
            'profit_share_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '10.00',
                'step': '0.01'
            }),
        }


class DepositForm(forms.ModelForm):
    """Form for recording deposits with dynamic month selection"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically generate month choices for current year and next 2 years
        current_year = datetime.now().year
        
        month_choices = [('', '--------- Select Month ---------')]
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        # Generate months for current year and next 2 years (3 years total)
        for year in range(current_year, current_year + 3):
            for month in month_names:
                month_choices.append((f'{month} {year}', f'{month} {year}'))
        
        self.fields['month'] = forms.ChoiceField(
            choices=month_choices,
            widget=forms.Select(attrs={'class': 'form-input'}),
            required=True
        )
    
    class Meta:
        model = Deposit
        fields = ['member', 'amount', 'deposit_date', 'month', 'notes']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'deposit_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }


class ProjectForm(forms.ModelForm):
    """Form for adding/editing projects"""
    class Meta:
        model = Project
        fields = ['name', 'project_type', 'description', 'start_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Project Name'
            }),
            'project_type': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Project Description'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
        }


class InvestmentForm(forms.ModelForm):
    """Form for recording investments"""
    class Meta:
        model = Investment
        fields = [
            'project', 
            'amount', 
            'investment_date', 
            'recipient',
            'purpose', 
            'is_returned', 
            'return_date', 
            'return_amount', 
            'notes'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'investment_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'recipient': forms.Select(attrs={'class': 'form-input'}), 
            'purpose': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'কেন টাকা নিচ্ছে - যেমন: ছাগল কিনতে, জমি কিনতে'
            }),
            'is_returned': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'return_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'return_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Additional notes'
            }),
        }


class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    class Meta:
        model = Payment
        fields = ['member', 'amount', 'payment_date', 'payment_type', 'notes']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'payment_type': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }


class ProfitForm(forms.ModelForm):
    """Form for recording profits with dynamic month selection"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically generate month choices for current year and next 2 years
        current_year = datetime.now().year
        
        month_choices = [('', '--------- Select Month ---------')]
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        # Generate months for current year and next 2 years (3 years total)
        for year in range(current_year, current_year + 3):
            for month in month_names:
                month_choices.append((f'{month} {year}', f'{month} {year}'))
        
        self.fields['month'] = forms.ChoiceField(
            choices=month_choices,
            widget=forms.Select(attrs={'class': 'form-input'}),
            required=False
        )
    
    class Meta:
        model = Profit
        fields = ['project', 'amount', 'profit_date', 'month', 'notes']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'profit_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }