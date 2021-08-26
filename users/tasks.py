from __future__ import absolute_import, unicode_literals
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils.translation import gettext as _
from core.celery import app as celery_app
from .models import User
from core.services import sms


@celery_app.task(
    name="tasks.debug_task", default_retry_delay=5, max_retries=5
)
def debug_task(message):
    print('Payload: {0!r}'.format(message))


@celery_app.task(
    name="tasks.send_very_sms", default_retry_delay=5, max_retries=5
)
def send_very_sms(phone, secret):
    body = "{} is your Django Boilerplateconfirmation code".format(secret)
    sms.send_message(phone, body)


@celery_app.task(
    name="tasks.send_restore_password_code", default_retry_delay=5,
    max_retries=5
)
def send_restore_password_code(phone, secret):
    body = "{} is your Django Boilerplateaccount restore code".format(secret)
    sms.send_message(phone, body)

@celery_app.task(
    name="tasks.send_socket_message", default_retry_delay=5, max_retries=5
)
def send_socket_message(topic, message):
    from core.socket_utils import send_socket_message

    send_socket_message('operator', topic, message)


@celery_app.task(
    name="tasks.send_welcome_email", default_retry_delay=5,
    max_retries=5
)
def send_welcome_email(user_id):
    user = User.objects.get(pk=user_id)
    html = f'<p>Hi {user.name},\n</p><p>Welcome to Bronse Trident. We are on-demand breakdown support' \
           ' network that will be ready to help you when you breakdown. Here is what you will get with Bronse Trident.</p>' \
           '<ul type="disc" style="margin-bottom:0cm;margin-top:0cm">' \
           '<li style="margin-left:15px;color:black;margin-top:0cm;margin-bottom:0.0001pt;vertical-align:baseline">' \
           '<span style="font-family:Arial,sans-serif">Instant cover when you download the Django Boilerplateapp' \
           '<u></u><u></u></span></li>' \
           '<li style="margin-left:15px;color:black;margin-top:0cm;margin-bottom:0.0001pt;vertical-align:baseline">' \
           '<span style="font-family:Arial,sans-serif">Getting a breakdown mechanic to you within 60 minutes<u></u>' \
           '<u>' \
           '</u></span></li>' \
           '<li style="margin-left:15px;color:black;margin-top:0cm;margin-bottom:0.0001pt;vertical-align:baseline">' \
           '<span style="font-family:Arial,sans-serif">Up to half an hour of mechanical support to fix the issue<u>' \
           '</u>' \
           '<u></u></span></li>' \
           '<li style="margin-left:15px;color:black;margin-top:0cm;margin-bottom:0.0001pt;vertical-align:baseline">' \
           '<span style="font-family:Arial,sans-serif">A tow of your vehicle to the nearest garage or within 10 miles' \
           '<u></u><u></u></span></li>' \
           '<li style="margin-left:15px;color:black;margin-top:0cm;margin-bottom:0.0001pt;vertical-align:baseline">' \
           '<span style="font-family:Arial,sans-serif">In-app updates with an estimated time of operator arrival<u>' \
           '</u><u></u></span></li>' \
           '<li style="margin-left:15px;color:black;margin-top:0cm;margin-bottom:0.0001pt;vertical-align:baseline">' \
           '<span style="font-family:Arial,sans-serif">24/7 UK-based telephone support centre' \
           '<u></u><u></u></span></li>' \
           '<li style="margin-left:15px;color:black;margin-top:0cm;margin-bottom:15pt;vertical-align:baseline">' \
           '<span style="font-family:Arial,sans-serif">Nationwide coverage including home recovery<u></u><u>' \
           '</u></span>' \
           '</li></ul>' \
           '<p>Should you have any issues with your vehicle or need any roadside assistance,\n' \
           ' simply launch the django  app and we will contact you as soon as possible. ' \
           'If you have any queries you can contact us via email at info@django_boilerplate.co.uk or call us on 0330 043 1309.' \
           '</p> ' \
           '<p>We look forward to being at your side 24/7.</p> ' \
           '<p>Safe driving!</p ' \
           '<p>The Django BoilerplateTeam.</p> '

    send_mail(
        _("Welcome to Bronse Trident"),
        _(
            f"Hi {user.name},\n"
        ),
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
        auth_user=None,
        auth_password=None,
        connection=None,
        html_message=html
    )

@celery_app.task(
    name="tasks.send_restore_email", default_retry_delay=5,
    max_retries=5
)
def send_restore_email(email, code):
    send_mail(
        _("Password Restore"),
        _(
            f"To confirm account restore process,\n"
            f"please enter this code  {code}\n"
        ),
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
