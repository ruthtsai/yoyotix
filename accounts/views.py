# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '註冊成功，已自動登入！')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next')
    if next_url:
        messages.info(request, '請先登入')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            password = form.cleaned_data['password']
            remember = request.POST.get('remember')  # 取得 checkbox 值

            # 嘗試登入
            user = authenticate(request, username=account, password=password)
            if user is None:
                try:
                    user_obj = User.objects.get(email=account)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)

                # 加入記住我設定
                if remember:
                    # 2 週內不用重新登入（1209600 秒）
                    request.session.set_expiry(1209600)
                else:
                    # 瀏覽器關閉就自動登出
                    request.session.set_expiry(0)

                messages.success(request, '登入成功，歡迎回來！')
                return redirect('/')
            else:
                messages.warning(request, '帳號/Email 或密碼錯誤，請再試一次。')
        else:
            messages.warning(request, '請確認輸入的資料格式正確。')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

# @login_required 是 Django 提供的裝飾器，用來限制該視圖（view）只能由已登入的使用者訪問。
@login_required(login_url='login')
def profile(request):
    user = request.user

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, '個人資料已更新。')
                return redirect('profile')

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, '密碼已更新。')
                return redirect('profile')
            else:
                messages.error(request, '請確認密碼輸入是否正確。')

    else:
        profile_form = ProfileUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'accounts/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })

# 刪除帳號
@login_required(login_url='login')
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "帳號已成功刪除，再見了！")
        return redirect('index')  # 或導向登入頁/login
    else:
        return redirect('/user/profile')