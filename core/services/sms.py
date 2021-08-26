from twilio.rest import Client
from core.settings import PHONE_PREFIX

account_sid = 'AC46a56ed53214fa4d5687036f34ce07a5'
auth_token = '58a2b65ac7d99ef428f55d518b7095f0'
client = Client(account_sid, auth_token)

phone_prefixes = {'UA': '+38', 'UK': '+44'}


def send_message(phone, body):
    number = f"{phone_prefixes[PHONE_PREFIX]}{phone}"
    message = client.messages \
        .create(
             body=body,
             from_='+441892803003',
             to=number
         )
    return message


def lookup(phone):
    try:
        number = f"{phone_prefixes[PHONE_PREFIX]}{phone}"
        phone_number = client.lookups \
            .phone_numbers(number) \
            .fetch()
    except Exception as e:
        print(e)
        phone_number = False

    return phone_number
