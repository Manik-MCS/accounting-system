from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime

class Member(models.Model):
    """Member model for Cooperative Society/DPS system"""
    member_id = models.CharField(max_length=50, unique=True, verbose_name="Member ID")
    name = models.CharField(max_length=200, verbose_name="Name")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    join_date = models.DateField(auto_now_add=True, verbose_name="Join Date")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    profit_share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        verbose_name="Profit Share %"
    )
    
    class Meta:
        ordering = ['member_id']
        verbose_name = "Member"
        verbose_name_plural = "Members"
    
    def __str__(self):
        return f"{self.member_id} - {self.name}"
    
    def get_total_deposits(self):
        """Calculate total deposits for this member"""
        return self.deposits.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def get_total_payments(self):
        """Calculate total payments received by this member"""
        return self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def get_balance(self):
        """Calculate balance (deposits - payments)"""
        return self.get_total_deposits() - self.get_total_payments()
    
    def get_profit_share(self):
        """Calculate profit share for this member"""
        return self.get_total_deposits() * (self.profit_share_percentage / 100)


class Project(models.Model):
    """Investment Project model (Goat farming, Land, etc.)"""
    PROJECT_TYPES = [
        ('goat_farming', 'Goat Farming'),
        ('land', 'Land Investment'),
        ('poultry', 'Poultry Farming'),
        ('fish', 'Fish Farming'),
        ('cow', 'Cow Farming'),
        ('agriculture', 'Agriculture'),
        ('shop', 'Shop/Retail Business'),
        ('transport', 'Transport Business'),
        ('real_estate', 'Real Estate'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Project Name")
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPES, default='other', verbose_name="Project Type")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    start_date = models.DateField(verbose_name="Start Date")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Project"
        verbose_name_plural = "Projects"
    
    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"
    
    def get_total_investment(self):
        """Calculate total investment in this project"""
        return self.investments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def get_total_profit(self):
        """Calculate total profit from this project"""
        return self.profits.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    def get_total_returned(self):
        """Calculate total returned amount from investments"""
        return self.investments.filter(is_returned=True).aggregate(
            total=models.Sum('return_amount')
        )['total'] or Decimal('0.00')
    
    def get_net_investment(self):
        """Calculate net investment (total invested - total returned)"""
        return self.get_total_investment() - self.get_total_returned()


class Recipient(models.Model):
    """
    Recipient model: যাদেরকে টাকা ইনভেস্ট বা লোন দেওয়া হচ্ছে
    (যেমন: জমির মালিক, ছাগল বিক্রেতা, ইত্যাদি)
    """
    name = models.CharField(max_length=200, verbose_name="Recipient Name")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    nid = models.CharField(max_length=50, blank=True, null=True, verbose_name="NID")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recipient"
        verbose_name_plural = "Recipients"

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Deposit(models.Model):
    """Monthly deposit records"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='deposits', verbose_name="Member")
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Amount"
    )
    deposit_date = models.DateField(verbose_name="Deposit Date")
    month = models.CharField(max_length=20, verbose_name="Month")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-deposit_date', '-created_at']
        verbose_name = "Deposit"
        verbose_name_plural = "Deposits"
        unique_together = ['member', 'month']
    
    def __str__(self):
        return f"{self.member.member_id} - {self.month} - ৳{self.amount}"


class Investment(models.Model):
    """Investment records in projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='investments', verbose_name="Project")
    
    # Investment Amount
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Investment Amount"
    )
    investment_date = models.DateField(verbose_name="Investment Date")
    
    # LINK TO RECIPIENT
    recipient = models.ForeignKey(
        Recipient, 
        on_delete=models.PROTECT, 
        verbose_name="Recipient (টাকা গ্রহণকারী)",
        null=True,
        blank=True
    )
    
    purpose = models.CharField(max_length=300, blank=True, null=True, verbose_name="Purpose (কেন নিচ্ছে)")
    
    # Return Information
    is_returned = models.BooleanField(default=False, verbose_name="Is Returned")
    return_date = models.DateField(blank=True, null=True, verbose_name="Return Date")
    return_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Return Amount"
    )
    
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-investment_date', '-created_at']
        verbose_name = "Investment"
        verbose_name_plural = "Investments"
    
    def __str__(self):
        if self.recipient:
            return f"{self.project.name} - {self.recipient.name} - ৳{self.amount}"
        else:
            return f"{self.project.name} - Unknown Recipient - ৳{self.amount}"
    
    def get_profit(self):
        """Calculate profit from this investment"""
        if self.is_returned and self.return_amount:
            return self.return_amount - self.amount
        return Decimal('0.00')
    
    def get_roi_percentage(self):
        """Calculate ROI percentage for this investment"""
        if self.is_returned and self.return_amount and self.amount > 0:
            profit = self.return_amount - self.amount
            return (profit / self.amount) * 100
        return Decimal('0.00')
    
    def get_days_running(self):
        """Calculate how many days investment is running"""
        from datetime import date
        if self.is_returned and self.return_date:
            return (self.return_date - self.investment_date).days
        return (date.today() - self.investment_date).days


class Profit(models.Model):
    """Profit/Interest records from projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='profits', verbose_name="Project")
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Profit Amount"
    )
    profit_date = models.DateField(verbose_name="Profit Date")
    month = models.CharField(max_length=20, blank=True, null=True, verbose_name="Month")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-profit_date', '-created_at']
        verbose_name = "Profit"
        verbose_name_plural = "Profits"
    
    def __str__(self):
        return f"{self.project.name} - ৳{self.amount} - {self.profit_date}"


class Payment(models.Model):
    """Payment records to members (withdrawals, profit distribution, etc.)"""
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments', verbose_name="Member")
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Payment Amount"
    )
    payment_date = models.DateField(verbose_name="Payment Date")
    payment_type = models.CharField(
        max_length=50,
        choices=[
            ('withdrawal', 'Withdrawal - টাকা তোলা'),
            ('profit', 'Profit Distribution - লাভ বিতরণ'),
            ('interest', 'Interest Payment - সুদ প্রদান'),
            ('loan', 'Loan Payment - ঋণ পরিশোধ'),
            ('salary', 'Salary - বেতন'),
            ('bonus', 'Bonus - বোনাস'),
            ('commission', 'Commission - কমিশন'),
            ('feed', 'Feed Cost - খাবার খরচ'),
            ('medicine', 'Medicine - ওষুধ'),
            ('transport', 'Transport - পরিবহন'),
            ('labor', 'Labor Cost - শ্রমিক খরচ'),
            ('electricity', 'Electricity Bill - বিদ্যুৎ'),
            ('rent', 'Rent - ভাড়া'),
            ('maintenance', 'Maintenance - রক্ষণাবেক্ষণ'),
            ('tax', 'Tax - কর'),
            ('purchase', 'Purchase - ক্রয়'),
            ('repair', 'Repair - মেরামত'),
            ('fuel', 'Fuel - জ্বালানি'),
            ('other', 'Other - অন্যান্য'),
        ],
        default='withdrawal',
        verbose_name="Payment Type"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"{self.member.member_id} - ৳{self.amount} - {self.payment_date}"