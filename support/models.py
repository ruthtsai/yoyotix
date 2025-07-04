# support/models.py
from django.db import models

class Message(models.Model):
    HASHTAG_CHOICES = [
        ('ticketing', '購票'),
        ('pickup', '取票'),
        ('account', '會員相關'),
        ('else', '其他')
    ]

    name = models.CharField("暱稱（可留空）", max_length=100, blank=True)
    hashtag = models.CharField("類別", max_length=20, choices=HASHTAG_CHOICES, default='ticketing')
    content = models.TextField("留言內容")
    is_public = models.BooleanField("是否公開", default=False)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)

    def __str__(self):
        return f"{self.name if self.name else '匿名'}：{self.content[:10]}"
