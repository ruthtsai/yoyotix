# tickets/forms.py
from django import forms
from django.utils import timezone
from .models import Ticket

class TicketSelectionForm(forms.Form):
    ticket_id = forms.ChoiceField(
        label="票種",
        widget=forms.RadioSelect
    )
    quantity = forms.IntegerField(label="購買張數", min_value=1, initial=1)
    agree = forms.BooleanField(
        label="我已閱讀並同意服務條款與隱私權政策",
        required=True,
        error_messages={'required': '請先勾選同意條款與隱私權政策。'}
    )

    def __init__(self, *args, **kwargs):
        tickets = kwargs.pop('tickets', [])
        super().__init__(*args, **kwargs)

        now = timezone.now()

        choices = []
        for ticket in tickets:
            # 僅加入已開賣且尚有剩餘票數的票種
            if (ticket.start_time is None or ticket.start_time <= now) and ticket.remaining > 0:
                label = f"{ticket.name} - ${ticket.price}（剩餘 {ticket.remaining} 張）"
                choices.append((ticket.id, label))

        self.fields['ticket_id'].choices = choices
