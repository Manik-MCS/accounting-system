from django.contrib import admin
from .models import Member, Deposit, Project, Investment, Profit, Payment, Recipient

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Customized Member Admin"""
    list_display = ['member_id', 'name', 'phone', 'profit_share_percentage', 'join_date', 'is_active', 'get_balance_display']
    list_filter = ['is_active', 'join_date']
    search_fields = ['member_id', 'name', 'phone', 'email']
    readonly_fields = ['join_date']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('member_id', 'name', 'phone', 'email')
        }),
        ('Address', {
            'fields': ('address',),
            'classes': ('collapse',)
        }),
        ('Profit Settings', {
            'fields': ('profit_share_percentage',)
        }),
        ('Status', {
            'fields': ('is_active', 'join_date')
        }),
    )
    
    def get_balance_display(self, obj):
        """Display member balance in list"""
        balance = obj.get_balance()
        if balance >= 0:
            return f"৳{balance:,.2f}"
        else:
            return f"-৳{abs(balance):,.2f}"
    get_balance_display.short_description = 'Balance'


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    """Customized Deposit Admin"""
    list_display = ['member', 'amount', 'month', 'deposit_date', 'created_at']
    list_filter = ['deposit_date', 'month']
    search_fields = ['member__member_id', 'member__name', 'month']
    date_hierarchy = 'deposit_date'
    readonly_fields = ['created_at']
    list_per_page = 100
    
    fieldsets = (
        ('Member & Amount', {
            'fields': ('member', 'amount')
        }),
        ('Date Information', {
            'fields': ('deposit_date', 'month')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Autocomplete for member selection
    autocomplete_fields = ['member']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Customized Project Admin"""
    list_display = ['name', 'project_type', 'start_date', 'get_investment_display', 'get_profit_display', 'is_active']
    list_filter = ['project_type', 'is_active', 'start_date']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'get_total_investment', 'get_total_profit']
    date_hierarchy = 'start_date'
    list_per_page = 50
    
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'project_type', 'start_date')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Financial Summary', {
            'fields': ('get_total_investment', 'get_total_profit'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
    
    def get_investment_display(self, obj):
        """Display total investment"""
        return f"৳{obj.get_total_investment():,.2f}"
    get_investment_display.short_description = 'Total Investment'
    
    def get_profit_display(self, obj):
        """Display total profit"""
        return f"৳{obj.get_total_profit():,.2f}"
    get_profit_display.short_description = 'Total Profit'


# --- নতুন Recipient Admin যোগ করা হয়েছে ---
@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Customized Recipient Admin"""
    list_display = ['name', 'phone', 'nid', 'created_at']
    search_fields = ['name', 'phone', 'nid']
    list_per_page = 50

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'phone', 'nid')
        }),
        ('Address', {
            'fields': ('address',),
        }),
    )


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    """Customized Investment Admin"""
    list_display = ['project', 'recipient', 'amount', 'investment_date', 'created_at']
    list_filter = ['investment_date', 'project']
    search_fields = ['project__name', 'notes', 'recipient__name']
    date_hierarchy = 'investment_date'
    readonly_fields = ['created_at']
    list_per_page = 100
    
    fieldsets = (
        ('Investment Details', {
            'fields': ('project', 'recipient', 'amount', 'investment_date')
        }),
        ('Return Info', {
            'fields': ('is_returned', 'return_date', 'return_amount', 'purpose')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    autocomplete_fields = ['project', 'recipient']


@admin.register(Profit)
class ProfitAdmin(admin.ModelAdmin):
    """Customized Profit Admin"""
    list_display = ['project', 'amount', 'profit_date', 'month', 'created_at']
    list_filter = ['profit_date', 'project', 'month']
    search_fields = ['project__name', 'notes', 'month']
    date_hierarchy = 'profit_date'
    readonly_fields = ['created_at']
    list_per_page = 100
    
    fieldsets = (
        ('Profit Details', {
            'fields': ('project', 'amount', 'profit_date', 'month')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    autocomplete_fields = ['project']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Customized Payment Admin"""
    list_display = ['member', 'amount', 'payment_type', 'payment_date', 'created_at']
    list_filter = ['payment_type', 'payment_date']
    search_fields = ['member__member_id', 'member__name', 'notes']
    date_hierarchy = 'payment_date'
    readonly_fields = ['created_at']
    list_per_page = 100
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('member', 'amount', 'payment_type', 'payment_date')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    autocomplete_fields = ['member']


# Customize Admin Site Header
admin.site.site_header = "ALORON Accounting System"
admin.site.site_title = "ALORON Admin"
admin.site.index_title = "Welcome to ALORON Accounting System"