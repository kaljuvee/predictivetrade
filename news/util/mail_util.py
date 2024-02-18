import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP server configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # or 465 for SSL
smtp_user = 'kaljuvee@gmail.com'
smtp_password = 'kdhw pvlr dmmi cbxr'

# Email parameters
from_addr = 'info@predictivelabs.co.uk'
to_addr = 'kaljuvee@gmail.com'


def send_mail(from_addr, to_addr, subject, body):
    # Create MIME message
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        print('Attempting to send email')
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)
        server.quit()
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')

def main():
    subject = 'Trading alert'
    body = 'Please check trading news.'
    send_mail(from_addr, to_addr, subject, body)
if __name__ == '__main__':
    main()