from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_templated_email(subject, template_name, context, recipients, from_email=None):
    html_message = render_to_string(template_name, context)
    text_message = strip_tags(html_message)
    email = EmailMultiAlternatives(subject, text_message, from_email, recipients)
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)