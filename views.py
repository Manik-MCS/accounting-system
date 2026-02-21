from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, Count
from django.http import JsonResponse
from django.contrib import messages  # ✅ Already imported
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Member, Deposit, Project, Investment, Profit, Payment, Recipient
from .forms import MemberForm, DepositForm, ProjectForm, InvestmentForm, PaymentForm, ProfitForm, RecipientForm


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome {username}!')  # ✅ Already added
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')  # ✅ Already added
        else:
            messages.error(request, 'Invalid username or password.')  # ✅ Already added
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'accounts/login.html', context)


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')  # ✅ Already added
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """Main dashboard with summary statistics"""
    total_members = Member.objects.filter(is_active=True).count()
    total_deposits = Deposit.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_investments = Investment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_profits = Profit.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    balance = total_deposits - total_payments
    
    context = {
        'total_members': total_members,
        'total_deposits': total_deposits,
        'total_investments': total_investments,
        'total_profits': total_profits,
        'total_payments': total_payments,
        'balance': balance,
    }
    return render(request, 'accounts/dashboard.html', context)


# --- Recipient Management (যাকে টাকা দিবেন তার জন্য) ---

@login_required(login_url='login')
def recipient_list(request):
    """যাদের টাকা দেওয়া হচ্ছে তাদের তালিকা"""
    recipients = Recipient.objects.all().order_by('-created_at')
    return render(request, 'accounts/recipient_list.html', {'recipients': recipients})


@login_required(login_url='login')
def recipient_add(request):
    """নতুন বিনিয়োগ গ্রহণকারী যুক্ত করা"""
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save()  # ✅ recipient variable save করুন
            messages.success(request, f'{recipient.name} সফলভাবে যুক্ত করা হয়েছে!')  # ✅ ADD THIS
            return redirect('recipient_list')
    else:
        form = RecipientForm()
    
    context = {
        'form': form,
        'title': 'Add New Recipient'
    }
    return render(request, 'accounts/recipient_form.html', context)


@login_required(login_url='login')
def recipient_detail(request, pk):
    """বিনিয়োগ গ্রহণকারীর বিস্তারিত তথ্য ও লেনদেন হিস্ট্রি"""
    recipient = get_object_or_404(Recipient, pk=pk)
    investments = Investment.objects.filter(recipient=recipient).order_by('-investment_date')
    
    context = {
        'recipient': recipient,
        'investments': investments,
    }
    return render(request, 'accounts/recipient_detail.html', context)


@login_required(login_url='login')
def member_list(request):
    """List all members with their financial summary"""
    members = Member.objects.filter(is_active=True).annotate(
        total_deposits=Sum('deposits__amount'),
        total_payments=Sum('payments__amount')
    )
    
    # Get total company profit once
    total_company_profit = Profit.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    for member in members:
        member.total_deposits = member.total_deposits or Decimal('0.00')
        member.total_payments = member.total_payments or Decimal('0.00')
        member.balance = member.total_deposits - member.total_payments
        member.profit_share = (total_company_profit * member.profit_share_percentage) / 100
        member.final_balance = member.balance + member.profit_share
    
    context = {
        'members': members,
        'total_company_profit': total_company_profit,
    }
    return render(request, 'accounts/member_list.html', context)


@login_required(login_url='login')
def member_detail(request, member_id):
    """Member detail view with deposits and payments"""
    # ✅ FIX THIS FUNCTION - এটি ঠিক করতে হবে
    member = get_object_or_404(Member, member_id=member_id)
    
    deposits = Deposit.objects.filter(member=member).order_by('-deposit_date')
    payments = Payment.objects.filter(member=member).order_by('-payment_date')
    
    total_deposits = member.get_total_deposits()
    total_payments = member.get_total_payments()
    balance = member.get_balance()
    
    context = {
        'member': member,
        'deposits': deposits,
        'payments': payments,
        'total_deposits': total_deposits,
        'total_payments': total_payments,
        'balance': balance,
    }
    return render(request, 'accounts/member_detail.html', context)


@login_required(login_url='login')
def project_list(request):
    """List all projects with investment and profit summary"""
    projects = Project.objects.filter(is_active=True)
    
    projects_data = []
    for project in projects:
        total_inv = project.get_total_investment()
        total_prof = project.get_total_profit()
        total_ret = project.get_total_returned()
        net_inv = project.get_net_investment()
        
        # Calculate ROI
        if total_inv > 0:
            roi = (total_prof / total_inv) * 100
        else:
            roi = 0
        
        projects_data.append({
            'id': project.id,
            'name': project.name,
            'project_type': project.get_project_type_display(),
            'start_date': project.start_date,
            'total_investment': total_inv,
            'total_returned': total_ret,
            'net_investment': net_inv,
            'total_profit': total_prof,
            'roi': roi,
            'is_active': project.is_active,
        })
    
    context = {
        'projects': projects_data,
    }
    return render(request, 'accounts/project_list.html', context)


@login_required(login_url='login')
def project_detail(request, project_id):
    """Project detail view with all investments and profits"""
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found!')  # ✅ ADD THIS
        return redirect('project_list')
    
    investments = project.investments.all().order_by('-investment_date')
    profits = project.profits.all().order_by('-profit_date')
    
    context = {
        'project': project,
        'investments': investments,
        'profits': profits,
        'total_investment': project.get_total_investment(),
        'total_profit': project.get_total_profit(),
    }
    return render(request, 'accounts/project_detail.html', context)


@login_required(login_url='login')
def reports(request):
    """Advanced reports page with filtering"""
    report_type = request.GET.get('report_type', 'summary')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    member_id = request.GET.get('member_id', '')
    project_id = request.GET.get('project_id', '')
    
    total_members = Member.objects.filter(is_active=True).count()
    total_deposits = Deposit.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_investments = Investment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_returned = Investment.objects.filter(is_returned=True).aggregate(total=Sum('return_amount'))['total'] or Decimal('0.00')
    total_profits = Profit.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    monthly_deposits = Deposit.objects.values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-month')[:12]
    
    members_summary = []
    members = Member.objects.filter(is_active=True)
    if member_id:
        members = members.filter(member_id=member_id)
    
    for member in members:
        deposits_query = member.deposits.all()
        payments_query = member.payments.all()
        
        if start_date:
            deposits_query = deposits_query.filter(deposit_date__gte=start_date)
            payments_query = payments_query.filter(payment_date__gte=start_date)
        if end_date:
            deposits_query = deposits_query.filter(deposit_date__lte=end_date)
            payments_query = payments_query.filter(payment_date__lte=end_date)
        
        total_dep = deposits_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_pay = payments_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        members_summary.append({
            'member_id': member.member_id,
            'name': member.name,
            'total_deposits': total_dep,
            'total_payments': total_pay,
            'balance': total_dep - total_pay,
        })
    
    projects_summary = []
    projects = Project.objects.filter(is_active=True)
    if project_id:
        projects = projects.filter(id=project_id)
    
    for project in projects:
        investments_query = project.investments.all()
        profits_query = project.profits.all()
        
        if start_date:
            investments_query = investments_query.filter(investment_date__gte=start_date)
            profits_query = profits_query.filter(profit_date__gte=start_date)
        if end_date:
            investments_query = investments_query.filter(investment_date__lte=end_date)
            profits_query = profits_query.filter(profit_date__lte=end_date)
        
        total_inv = investments_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_ret = investments_query.filter(is_returned=True).aggregate(total=Sum('return_amount'))['total'] or Decimal('0.00')
        total_prof = profits_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        net_inv = total_inv - total_ret
        roi = (total_prof / total_inv * 100) if total_inv > 0 else 0
        
        projects_summary.append({
            'id': project.id,
            'name': project.name,
            'project_type': project.get_project_type_display(),
            'total_investment': total_inv,
            'total_returned': total_ret,
            'net_investment': net_inv,
            'total_profit': total_prof,
            'roi': roi,
        })
    
    transactions = []
    if report_type == 'transactions':
        deposits = Deposit.objects.all()
        if member_id:
            deposits = deposits.filter(member__member_id=member_id)
        if start_date:
            deposits = deposits.filter(deposit_date__gte=start_date)
        if end_date:
            deposits = deposits.filter(deposit_date__lte=end_date)
        
        for dep in deposits.order_by('-deposit_date')[:100]:
            transactions.append({
                'date': dep.deposit_date,
                'type': 'Deposit',
                'member': dep.member.name,
                'amount': dep.amount,
                'notes': dep.notes or '-',
            })
        
        payments = Payment.objects.all()
        if member_id:
            payments = payments.filter(member__member_id=member_id)
        if start_date:
            payments = payments.filter(payment_date__gte=start_date)
        if end_date:
            payments = payments.filter(payment_date__lte=end_date)
        
        for pay in payments.order_by('-payment_date')[:100]:
            transactions.append({
                'date': pay.payment_date,
                'type': f'Payment ({pay.get_payment_type_display()})',
                'member': pay.member.name,
                'amount': -pay.amount,
                'notes': pay.notes or '-',
            })
        
        transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)[:100]
    
    context = {
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
        'member_id': member_id,
        'project_id': project_id,
        'total_members': total_members,
        'total_deposits': total_deposits,
        'total_investments': total_investments,
        'total_returned': total_returned,
        'total_profits': total_profits,
        'total_payments': total_payments,
        'balance': total_deposits - total_payments,
        'monthly_deposits': monthly_deposits,
        'members_summary': members_summary,
        'projects_summary': projects_summary,
        'transactions': transactions,
        'all_members': Member.objects.filter(is_active=True).order_by('member_id'),
        'all_projects': Project.objects.filter(is_active=True).order_by('name'),
    }
    return render(request, 'accounts/reports.html', context)


@login_required(login_url='login')
def member_add(request):
    """Add new member"""
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member {member.name} added successfully!')  # ✅ Already added
            return redirect('member_detail', member_id=member.member_id)
    else:
        form = MemberForm()
    
    context = {
        'form': form,
        'title': 'Add New Member'
    }
    return render(request, 'accounts/member_form.html', context)


@login_required(login_url='login')
def deposit_add(request):
    """Record new deposit"""
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save()
            messages.success(request, f'Deposit of ৳{deposit.amount} recorded successfully!')  # ✅ Already added
            return redirect('deposit_receipt', deposit_id=deposit.id)
    else:
        form = DepositForm()
    
    context = {
        'form': form,
        'title': 'Record Deposit'
    }
    return render(request, 'accounts/deposit_form.html', context)


@login_required(login_url='login')
def deposit_receipt(request, deposit_id):
    """Generate deposit receipt"""
    deposit = get_object_or_404(Deposit, id=deposit_id)
    context = {
        'deposit': deposit,
    }
    return render(request, 'accounts/deposit_receipt.html', context)


@login_required(login_url='login')
def project_add(request):
    """Add new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project {project.name} created successfully!')  # ✅ Already added
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': 'Add New Project'
    }
    return render(request, 'accounts/project_form.html', context)


@login_required(login_url='login')
def investment_add(request):
    """Record new investment"""
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save()
            messages.success(request, f'Investment of ৳{investment.amount} recorded successfully!')  # ✅ Already added
            return redirect('project_detail', project_id=investment.project.id)
    else:
        form = InvestmentForm()
    
    context = {
        'form': form,
        'title': 'Record Investment'
    }
    return render(request, 'accounts/investment_form.html', context)


@login_required(login_url='login')
def payment_add(request):
    """Record new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment of ৳{payment.amount} recorded successfully!')  # ✅ Already added
            return redirect('payment_receipt', payment_id=payment.id)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'title': 'Record Payment'
    }
    return render(request, 'accounts/payment_form.html', context)


@login_required(login_url='login')
def payment_receipt(request, payment_id):
    """Generate payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id)
    context = {
        'payment': payment,
    }
    return render(request, 'accounts/payment_receipt.html', context)


@login_required(login_url='login')
def profit_add(request):
    """Record new profit"""
    if request.method == 'POST':
        form = ProfitForm(request.POST)
        if form.is_valid():
            profit = form.save()
            messages.success(request, f'Profit of ৳{profit.amount} recorded successfully!')  # ✅ Already added
            return redirect('project_detail', project_id=profit.project.id)
    else:
        form = ProfitForm()
    
    context = {
        'form': form,
        'title': 'Record Profit'
    }
    return render(request, 'accounts/profit_form.html', context)


@login_required(login_url='login')
def member_edit(request, member_id):
    """Edit existing member"""
    member = get_object_or_404(Member, member_id=member_id)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Member {member.name} updated successfully!')  # ✅ Already added
            return redirect('member_detail', member_id=member.member_id)
    else:
        form = MemberForm(instance=member)
    
    context = {
        'form': form,
        'title': f'Edit Member: {member.name}',
        'member': member,
    }
    return render(request, 'accounts/member_form.html', context)


@login_required(login_url='login')
def member_delete(request, member_id):
    """Delete member"""
    member = get_object_or_404(Member, member_id=member_id)
    if request.method == 'POST':
        member_name = member.name
        member.delete()
        messages.success(request, f'Member {member_name} deleted successfully!')  # ✅ Already added
        return redirect('member_list')
    
    context = {
        'member': member,
        'title': f'Delete Member: {member.name}',
    }
    return render(request, 'accounts/confirm_delete.html', context)


@login_required(login_url='login')
def project_edit(request, project_id):
    """Edit existing project"""
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project {project.name} updated successfully!')  # ✅ Already added
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'title': f'Edit Project: {project.name}',
        'project': project,
    }
    return render(request, 'accounts/project_form.html', context)


@login_required(login_url='login')
def project_delete(request, project_id):
    """Delete project"""
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project {project_name} deleted successfully!')  # ✅ Already added
        return redirect('project_list')
    
    context = {
        'project': project,
        'title': f'Delete Project: {project.name}',
    }
    return render(request, 'accounts/confirm_delete.html', context)


@login_required(login_url='login')
def deposit_delete(request, deposit_id):
    """Delete deposit"""
    deposit = get_object_or_404(Deposit, id=deposit_id)
    member_id = deposit.member.member_id
    if request.method == 'POST':
        amount = deposit.amount
        deposit.delete()
        messages.success(request, f'Deposit of ৳{amount} deleted successfully!')  # ✅ Already added
        return redirect('member_detail', member_id=member_id)
    
    context = {
        'object': deposit,
        'object_type': 'Deposit',
        'title': f'Delete Deposit',
    }
    return render(request, 'accounts/confirm_delete.html', context)


@login_required(login_url='login')
def payment_delete(request, payment_id):
    """Delete payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    member_id = payment.member.member_id
    if request.method == 'POST':
        amount = payment.amount
        payment.delete()
        messages.success(request, f'Payment of ৳{amount} deleted successfully!')  # ✅ Already added
        return redirect('member_detail', member_id=member_id)
    
    context = {
        'object': payment,
        'object_type': 'Payment',
        'title': f'Delete Payment',
    }
    return render(request, 'accounts/confirm_delete.html', context)


@login_required(login_url='login')
def investment_delete(request, investment_id):
    """Delete investment"""
    investment = get_object_or_404(Investment, id=investment_id)
    project_id = investment.project.id
    if request.method == 'POST':
        amount = investment.amount
        investment.delete()
        messages.success(request, f'Investment of ৳{amount} deleted successfully!')  # ✅ Already added
        return redirect('project_detail', project_id=project_id)
    
    context = {
        'object': investment,
        'object_type': 'Investment',
        'title': f'Delete Investment',
    }
    return render(request, 'accounts/confirm_delete.html', context)


@login_required(login_url='login')
def profit_delete(request, profit_id):
    """Delete profit"""
    profit = get_object_or_404(Profit, id=profit_id)
    project_id = profit.project.id
    if request.method == 'POST':
        amount = profit.amount
        profit.delete()
        messages.success(request, f'Profit of ৳{amount} deleted successfully!')  # ✅ Already added
        return redirect('project_detail', project_id=project_id)
    
    context = {
        'object': profit,
        'object_type': 'Profit',
        'title': f'Delete Profit',
    }
    return render(request, 'accounts/confirm_delete.html', context)