import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.models.user import UserProfile, Plan, PlanType
from typing import Optional

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.admin_email = settings.ADMIN_EMAIL

    async def send_upgrade_request_to_admin(self, user: UserProfile, message: Optional[str] = None) -> bool:
        """Send upgrade request notification to admin"""
        try:
            email_body = f"""
            New Pro Plan Upgrade Request

            User Details:
            - User ID: {user.id}
            - Email: {user.email}
            - Name: {user.full_name or 'Not provided'}
            - Company: {user.company or 'Not provided'}
            
            Current Plan Details:
            - Current Plan: {user.plan_type.value}
            - Current Credits: {user.credits}
            
            Pro Plan Details:
            - Credits: {Plan.get_pro_plan().credits}
            - Price: ${Plan.get_pro_plan().price_usd}

            Additional Message:
            {message or 'No additional message provided'}

            To approve this upgrade, use the admin dashboard or API endpoint:
            POST /user/upgrade-confirm/{user.id}
            """

            return await self._send_email(
                to_email=self.admin_email,
                subject=f"Pro Plan Upgrade Request - {user.email}",
                body=email_body
            )
        except Exception as e:
            print(f"Failed to send upgrade request email: {str(e)}")
            return False

    async def send_upgrade_request_received(self, user: UserProfile) -> bool:
        """Send confirmation to user that upgrade request was received"""
        try:
            email_body = f"""
            Hi {user.full_name or 'there'},

            We've received your request to upgrade to the Pro Plan.

            Pro Plan Benefits:
            - {Plan.get_pro_plan().credits} credits
            - More advanced features
            - Priority support

            Our team will review your request and process it shortly.
            We'll send you another email once your upgrade is confirmed.

            Current Plan Details:
            - Current Plan: {user.plan_type.value}
            - Current Credits: {user.credits}

            Thank you for choosing to upgrade!

            Best regards,
            LinkPulse Team
            """

            return await self._send_email(
                to_email=user.email,
                subject="We've Received Your Pro Plan Upgrade Request",
                body=email_body
            )
        except Exception as e:
            print(f"Failed to send request received email: {str(e)}")
            return False

    async def send_upgrade_confirmation(self, user: UserProfile) -> bool:
        """Send confirmation email when upgrade is complete"""
        try:
            email_body = f"""
            Congratulations {user.full_name or 'there'}!

            Your account has been successfully upgraded to the Pro Plan! 🎉

            Your New Plan Details:
            - Plan: Pro
            - Credits: {Plan.get_pro_plan().credits}
            - All Pro features are now unlocked

            You can start using your additional credits right away.
            If you have any questions, feel free to reach out to our support team.

            Thank you for upgrading to Pro!

            Best regards,
            LinkPulse Team
            """

            return await self._send_email(
                to_email=user.email,
                subject="Welcome to Pro Plan! 🎉",
                body=email_body
            )
        except Exception as e:
            print(f"Failed to send upgrade confirmation email: {str(e)}")
            return False

    async def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Internal method to send emails"""
        try:
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

email_service = EmailService() 