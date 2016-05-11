# What do we want?
# Function to mail one user
# Function to mail a set of users
# Basic mail template
# Reply-To header

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings

class Notification(object):
    sender_address = "USG Housing <housing@ju-u.sg>"
    mail_title = "Empty"

    txt_template = "notify/base.txt"
    html_template = "notify/base.html"

    def __init__(self, user):
        self.user = user

    def get_context(self):
        return {}

    def send(self):
        full_context = self.get_context()
        full_context['domain'] = settings.EMAIL_DOMAIN
        full_context['user'] = self.user

        msg_plain = render_to_string(self.txt_template, full_context)
        msg_html = render_to_string(self.html_template, full_context)

        send_mail(
            "USG Housing: " + self.mail_title,
            msg_plain,
            self.sender_address,
            [self.user.email],
            html_message=msg_html,
        )

class InboxNotification(Notification):
    mail_title = "New roommate request"
    txt_template = "notify/inbox.txt"
    html_template = "notify/inbox.html"

    def __init__(self, room_request):
        super(InboxNotification, self).__init__(room_request.receiver)
        self.room_request = room_request

    def get_context(self):
        return {'request': self.room_request}