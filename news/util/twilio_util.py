from twilio.rest import Client

def send_message(txt):
    account_sid = 'AC34a68f2862daadd1b07547cfabf0dc10'
    auth_token = '21f888994d57768bb4a7f70cb8e3b6b8'

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio WhatsApp number
        body=txt,                       # Text of the message
        to='whatsapp:+447585099329'     # Your WhatsApp number
    )

    return message.sid