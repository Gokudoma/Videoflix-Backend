from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_activation_email(email, activation_url):
    """
    Sends an account activation email to the user asynchronously.

    Args:
        email (str): The recipient's email address.
        activation_url (str): The complete URL for account activation.
    """
    subject = "Activate your Videoflix Account"
    

    html_message = render_to_string('authentication_app/activation_email.html', {
        'activation_url': activation_url,
        'app_name': "Videoflix"
    })
    

    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        plain_message,
        from_email,
        [email],
        html_message=html_message,
        fail_silently=False,
    )

def send_password_reset_email(email, reset_url):
    """
    Sends a password reset email to the user asynchronously.

    Args:
        email (str): The recipient's email address.
        reset_url (str): The complete URL for password reset.
    """
    subject = "Reset your Videoflix Password"
    

    html_message = render_to_string('authentication_app/password_reset_email.html', {
        'reset_url': reset_url,
        'app_name': "Videoflix"
    })
    

    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        plain_message,
        from_email,
        [email],
        html_message=html_message,
        fail_silently=False,
    )