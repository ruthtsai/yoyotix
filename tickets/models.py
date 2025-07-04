from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import uuid
import hashlib



class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="名稱")
    description = models.TextField(verbose_name="描述")
    main_image = models.ImageField(
    upload_to='events/',
    verbose_name="主視覺圖",
    default='events/default.png'  # 這裡是字串路徑，對應你 static 資料夾內的圖片路徑
)
    event_date = models.DateTimeField(verbose_name="演出日期")
    location = models.CharField(max_length=200, verbose_name="地點")
    organizer = models.CharField(max_length=200, verbose_name="主辦單位")
    seating_map = models.ImageField(upload_to='events/seating_maps/', null=True, blank=True, verbose_name="座位圖"  # 對應你 static 資料夾內的圖片路徑
)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    name = models.CharField(max_length=100, verbose_name="票種名稱", default="全票")  # 如「VIP票」、「一般票」
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="票價")
    quantity = models.PositiveIntegerField(verbose_name="座位數", default=0)  # 座位數量
    sold = models.PositiveIntegerField(default=0, verbose_name="已售張數")
    start_time = models.DateTimeField(verbose_name="開賣時間", default=timezone.now)  # 新增欄位

    def __str__(self):
        return f"{self.event.title} - {self.name} (${self.price})"

    # 例如在 Ticket model 中的 remaining 屬性計算前加入：
    def get_valid_orders(self):
        for order in self.orders.filter(status='pending'):
            order.auto_cancel_if_expired()
        return self.orders.exclude(status='cancelled')

    @property
    def remaining(self):
        if self.quantity is None or self.sold is None:
            return 0
        return self.quantity - self.sold

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '未結帳'),
        ('paid', '已結帳'),
        ('collected', '已取票'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=4)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(verbose_name="張數")  # 一次只能買一個價位的張數
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="狀態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return f"訂單 #{self.id} - {self.user.username} - {self.ticket.name} x {self.quantity}"

    def is_expired(self):
            if self.status == 'pending':
                expire_time = self.created_at + timedelta(minutes=15)
                return timezone.now() > expire_time
            return False

    def auto_cancel_if_expired(self):
        if self.is_expired():
            self.status = 'cancelled'
            self.save()

            # 將訂單數量從票券的 sold 中扣回來
            self.ticket.sold = max(self.ticket.sold - self.quantity, 0)
            self.ticket.save()

    def cancel_order(self):
        if self.status != 'cancelled':
            self.status = 'cancelled'
            self.ticket.sold = max(self.ticket.sold - self.quantity, 0)
            self.ticket.save()
            self.save()

# 驗票碼
class TicketCode(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ticket_codes')
    code = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"票碼：{self.code}"

    @staticmethod
    def generate_code():
        raw_uuid = uuid.uuid4().hex
        return hashlib.sha256(raw_uuid.encode()).hexdigest()[:20]  # 取前 20 碼即可