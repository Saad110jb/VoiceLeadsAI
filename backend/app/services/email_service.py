import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.utils.logger import logger

class EmailService:
    def __init__(self):
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_APP_PASSWORD
        self.receiver_email = settings.NOTIFICATION_RECEIVER

    def send_lead_notification(self, lead_data: dict) -> bool:
        """Sends an HTML formatted lead alert email to the notification receiver."""
        if not self.sender_email or not self.sender_password:
            logger.warning("SMTP credentials missing. Email notification skipped.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            temp = lead_data.get("lead_temperature", "WARM")
            badge_color = "#ef4444" if temp == "HOT" else ("#f59e0b" if temp == "WARM" else "#3b82f6")

            msg["Subject"] = f"🔥 [{temp} LEAD] New Voice Lead: {lead_data.get('name', 'Prospect')}"
            msg["From"] = f"VoiceLeads AI <{self.sender_email}>"
            msg["To"] = self.receiver_email

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #1e293b; border-radius: 12px; padding: 24px; border: 1px solid #334155;">
                    <h2 style="color: #38bdf8; margin-top: 0;">🎙️ VoiceLeads AI - New Lead Alert</h2>
                    
                    <div style="background: {badge_color}; color: white; display: inline-block; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 14px; margin-bottom: 16px;">
                        TEMPERATURE: {temp}
                    </div>

                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <tr><td style="padding: 8px; color: #94a3b8;"><strong>Name:</strong></td><td style="padding: 8px; color: #ffffff;">{lead_data.get('name', 'N/A')}</td></tr>
                        <tr><td style="padding: 8px; color: #94a3b8;"><strong>Email:</strong></td><td style="padding: 8px; color: #ffffff;">{lead_data.get('email', 'N/A')}</td></tr>
                        <tr><td style="padding: 8px; color: #94a3b8;"><strong>Phone:</strong></td><td style="padding: 8px; color: #ffffff;">{lead_data.get('phone', 'N/A')}</td></tr>
                        <tr><td style="padding: 8px; color: #94a3b8;"><strong>Company:</strong></td><td style="padding: 8px; color: #ffffff;">{lead_data.get('company', 'N/A')}</td></tr>
                        <tr><td style="padding: 8px; color: #94a3b8;"><strong>Budget:</strong></td><td style="padding: 8px; color: #ffffff;">{lead_data.get('budget', 'N/A')}</td></tr>
                        <tr><td style="padding: 8px; color: #94a3b8;"><strong>Timeframe:</strong></td><td style="padding: 8px; color: #ffffff;">{lead_data.get('timeframe', 'N/A')}</td></tr>
                        <tr><td style="padding: 8px; color: #94a3b8;"><strong>Intent:</strong></td><td style="padding: 8px; color: #ffffff;">{lead_data.get('intent', 'N/A')}</td></tr>
                    </table>

                    <div style="background: #0f172a; padding: 16px; border-radius: 8px; border-left: 4px solid #38bdf8; margin-bottom: 20px;">
                        <h4 style="margin: 0 0 8px 0; color: #38bdf8;">Call Summary</h4>
                        <p style="margin: 0; color: #cbd5e1;">{lead_data.get('summary', 'No summary available.')}</p>
                    </div>

                    <div style="text-align: center; color: #64748b; font-size: 12px; margin-top: 20px;">
                        Powered by VoiceLeads AI • VocalSync CRM Engine
                    </div>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, "html"))

            # Clean spaces from Gmail app password if needed
            clean_password = self.sender_password.replace(" ", "")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, clean_password)
                server.sendmail(self.sender_email, self.receiver_email, msg.as_string())

            logger.info(f"Lead alert email successfully sent to {self.receiver_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send lead notification email: {e}")
            return False

email_service = EmailService()
