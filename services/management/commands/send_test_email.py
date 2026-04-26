from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a test email to verify Gmail SMTP settings"

    def add_arguments(self, parser):
        parser.add_argument("recipient", help="Recipient email address for the test email")

    def handle(self, *args, **options):
        recipient = options["recipient"]
        subject = "SHMS SMTP Test Email"
        message = (
            "Hello,\n\n"
            "This is a test email from SHMS to verify Gmail SMTP configuration.\n\n"
            "If you received this message, the email setup is working correctly.\n\n"
            "SHMS Team"
        )

        try:
            sent_count = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(f"Failed to send test email: {exc}") from exc

        if sent_count:
            self.stdout.write(self.style.SUCCESS(f"Test email sent successfully to {recipient}"))
        else:
            raise CommandError("send_mail returned 0; no email was sent")
