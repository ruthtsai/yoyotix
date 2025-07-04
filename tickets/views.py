# tickets/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.utils.html import escape
from django.urls import reverse
from django.shortcuts import render
import random
from .models import Event, Ticket, Order, TicketCode
from .forms import TicketSelectionForm
from datetime import timedelta
from random import sample
# qrcode 相關
import qrcode
import base64
from io import BytesIO


def homepage(request):
    events = Event.objects.all().order_by('-event_date')
    return render(request, 'index.html', {'events': events})
    
def events(request):
    query = request.GET.get('q', '')
    if query:
        events = Event.objects.filter(title__icontains=query).order_by('-event_date')  # 日期由近到遠
    else:
        events = Event.objects.all().order_by('-event_date')  # 日期由近到遠
    return render(request, 'tickets/events.html', {'events': events, 'query': query})


# 活動詳情
def event_detail(request, evid):
    event = get_object_or_404(Event, id=evid)
    tickets = event.tickets.all().order_by('-price')
    now = timezone.now()  # 加入現在時間

    return render(request, 'tickets/event_detail.html', locals())

# 購票頁面
@login_required(login_url='login')
def event_registration(request, evid):
    try:
        event = Event.objects.get(id=evid)
        tickets = event.tickets.all().order_by('-price')
    except Event.DoesNotExist:
        raise Http404("找不到這個活動")

    # 過濾掉已過期但尚未取消的訂單
    for ticket in tickets:
        for order in ticket.orders.filter(status='pending'):
            order.auto_cancel_if_expired()

    # 判斷是否所有票券售完
    all_sold_out = all(ticket.remaining == 0 for ticket in tickets)

    now = timezone.now()

    not_yet_started = False
    if tickets and hasattr(tickets[0], 'start_time'):
        start_times = [t.start_time for t in tickets if t.start_time is not None]
        if start_times:
            not_yet_started = now < min(start_times)
        else:
            # 所有 start_time 都是 None
            not_yet_started = False
    else:
        not_yet_started = now < event.event_date  # fallback


    if request.method == 'POST':
        form = TicketSelectionForm(request.POST, tickets=tickets)
        if form.is_valid():
            # 你的原本 POST 邏輯（購票數量檢查、session 設定等）
            # ...
            ticket_id = int(form.cleaned_data['ticket_id'])
            quantity = form.cleaned_data['quantity']
            selected_ticket = get_object_or_404(Ticket, id=ticket_id, event=event)

            if quantity < 1 or quantity > 4:
                message = "一次最多只能購買 4 張票，請重新輸入正確張數。"
                escaped_message = escape(message)
                redirect_url = reverse('event_registration', kwargs={'evid': event.id})
                return HttpResponse(f"""
                    <script>
                        alert("{escaped_message}");
                        window.location.href = "{redirect_url}";
                    </script>
                """)

            if selected_ticket.remaining < quantity:
                message = random.choice([
                    "糟糕，有人搶先一步啦！",
                    "餘票不足。",
                    "目前沒有可購票券，請稍後再試。"
                ])
                escaped_message = escape(message)
                redirect_url = reverse('event_registration', kwargs={'evid': event.id})
                return HttpResponse(f"""
                    <script>
                        alert("{escaped_message}");
                        window.location.href = "{redirect_url}";
                    </script>
                """)

            # 儲存資訊進 session，並導向下一步
            request.session.pop('registration_data', None)
            request.session['registration_data'] = {
                'event_id': event.id,
                'ticket_id': ticket_id,
                'quantity': quantity,
                'user': {
                    'username': request.user.username,
                    'email': request.user.email,
                    'user_id': request.user.id,
                },
                'timestamp': timezone.now().isoformat(),
            }
            return redirect('event_registration_check', evid=event.id)
    else:
        form = TicketSelectionForm(tickets=tickets)

    return render(request, 'tickets/event_registration.html', locals())

# 訂單確認
@login_required(login_url='login')
def event_registration_check(request, evid):
    event = get_object_or_404(Event, id=evid)
    data = request.session.get('registration_data')

    if not data or data.get('event_id') != event.id:
        messages.error(request, "無法取得購票資訊，請重新選擇票券。")
        return redirect('event_registration', evid=evid)

    ticket = get_object_or_404(Ticket, id=data['ticket_id'], event=event)
    quantity = data['quantity']
    total_price = ticket.price * quantity  # 僅作為顯示用途

    if request.method == 'POST':
        if ticket.remaining < quantity:
            messages.error(request, "抱歉，票券餘量不足，請重新選擇。")
            return redirect('event_registration', evid=evid)

        order = Order.objects.create(
            user=request.user,
            ticket=ticket,
            quantity=quantity,
            status='pending',
        )

        ticket.sold += quantity
        ticket.save()

        request.session.pop('registration_data', None)
        return redirect('event_checkout', order_id=order.id)

    return render(request, 'tickets/registration_check.html', {
        'event': event,
        'ticket': ticket,
        'quantity': quantity,
        'total_price': total_price,
        'user_info': {
            'username': request.user.username,
            'email': request.user.email,
        },
    })

# 結帳頁面
@login_required(login_url='login')
def event_checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')

    # 從 order.ticket 拿票價，從 order 拿張數，計算總價
    total_price = order.ticket.price * order.quantity

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method not in ['credit_card', 'atm']:
            messages.error(request, "請選擇有效的付款方式。")
            return redirect('event_checkout', order_id=order.id)
        
        # 模擬付款流程（這邊只是示意，實務需串第三方支付）
        # 付款成功後更新訂單狀態
        order.status = 'paid'
        order.save()

        messages.success(request, f"付款成功！您選擇的付款方式為：{'信用卡' if payment_method == 'credit_card' else 'ATM 轉帳'}")
        # 導向付款成功頁或訂單詳情頁
        return redirect('order_detail', order_id=order.id)

    return render(request, 'tickets/checkout.html', locals())


# 票券資訊頁面
@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.auto_cancel_if_expired()  # 嘗試自動取消

    # 計算剩餘時間（秒）
    if order.status == 'pending':
        expire_time = order.created_at + timedelta(minutes=15)
        remaining_seconds = int((expire_time - timezone.now()).total_seconds())
        remaining_seconds = max(remaining_seconds, 0)  # 不要負數
    else:
        remaining_seconds = 0

    if request.method == 'POST':
        # 只有「已付款未取票」狀態可點選「取票」
        if order.status == 'paid' and 'collect_ticket' in request.POST:
            order.status = 'collected'
            order.save()
            # 產生對應票數的驗票碼
            for _ in range(order.quantity):
                TicketCode.objects.create(order=order, code=TicketCode.generate_code())

            # messages.success(request, "取票成功！")
            return redirect('order_detail', order_id=order.id)

        elif order.status in ['paid', 'collected'] and 'cancel_order' in request.POST:
            # 活動已開始則禁止退票
            if timezone.now() > order.ticket.event.event_date:
                messages.error(request, "活動已開始，無法退票。", extra_tags='popup')
            else:
                order.cancel_order()
                messages.warning(request, "票券已取消，已付款訂單費用將會扣除手續費後退回至您的帳戶。", extra_tags='popup')
            return redirect('order_detail', order_id=order.id)

    # 若已取票，產生 QR Code 資料
    qr_codes = []
    if order.status == 'collected':
        for ticket_code in order.ticket_codes.all():
            qr_codes.append({
                'code': ticket_code.code,
                'img_data': generate_qr_base64(ticket_code.code),
            })

    return render(request, 'tickets/order_detail.html', {
        'order': order,
        'event': order.ticket.event,
        'remaining_seconds': remaining_seconds,
        'qr_codes': qr_codes,  # 將 QR 資料傳入 template
    })

# 產生qrcode的方法
def generate_qr_base64(code):
    qr = qrcode.make(code)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

# 使用者訂單總覽頁面(訂單)
@login_required(login_url='login')
def user_order_list(request):
    orders = Order.objects.filter(user=request.user).select_related('ticket', 'ticket__event').order_by('-created_at')
    

    return render(request, 'tickets/user_order_list.html', locals())


# 使用者訂單總覽頁面（我的票券）
@login_required(login_url='login')
def user_order_list_ads(request):
    events = Event.objects.all()
    orders = Order.objects.filter(user=request.user).select_related('ticket', 'ticket__event').order_by('-created_at')
    # 找出所有尚在售票中的活動（含有尚有剩餘票券的 event）
    now = timezone.now()
    selling_events = Event.objects.filter(
        tickets__start_time__lte=now
    ).distinct()

    # 過濾掉所有票種都賣完的活動
    available_events = []
    for event in selling_events:
        for ticket in event.tickets.all():
            if ticket.remaining > 0:
                available_events.append(event)
                break  # 此活動有票就保留，不用檢查其他票種
    
    # 隨機選擇三個推薦活動
        recommend_events = sample(available_events, min(3, len(available_events)))



    return render(request, 'tickets/user_order_list_ads.html', locals())

# youtube頁面
def strategy(request):
    return render(request, 'tickets/strategy.html')