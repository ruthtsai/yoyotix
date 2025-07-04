"""yoyotix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
import accounts.views as accounts
import tickets.views as tickets
import support.views as support



urlpatterns = [
    path('admin/', admin.site.urls),
    #path('mobile/detail/<int:id>', mobile.detail, name='detail-url'),
    # 購票相關
    path("captcha/", include("captcha.urls")),
    path('', tickets.homepage, name='index'),
    path('events/', tickets.events, name='events'), # 活動總覽
    path('event/<int:evid>/detail/', tickets.event_detail, name='event_detail'), # 活動細節
    path('event/<int:evid>/registration/', tickets.event_registration, name='event_registration'), # 購票（需登入）
    path('event/<int:evid>/registration/check/', tickets.event_registration_check, name='event_registration_check'), # 訂單確認
    path('user/order/<int:order_id>/checkout/', tickets.event_checkout, name='event_checkout'), # 結帳頁面（需登入）
    path('user/order/<int:order_id>/', tickets.order_detail, name='order_detail'),  # 訂單詳情（需登入）
    path('user/order/', tickets.user_order_list, name='user_order_list'), #訂單總覽（需登入）
    path('user/tikets/', tickets.user_order_list_ads, name='user_order_list_ads'), #訂單總覽有推薦（需登入）
    # 騙人連結
    path('events/strategy', tickets.strategy, name='strategy'),  # 教學
    # 使用者相關
    path('user/register/', accounts.register, name='register'),# 註冊頁面
    path('user/login/', accounts.login_view, name='login'), # 登入頁面
    path('user/logout/', accounts.logout_view, name='logout'), # 登出動作
    path('user/profile/', accounts.profile, name='profile'),  # 會員中心（需登入）
    path('user/delete/', accounts.delete_account, name='delete_account'),  # 刪除帳號（需登入）
    # 客服中心留言
    path('contact/', support.contact_form, name='contact_form'),
    path('messages/', support.message_list, name='message_list'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
