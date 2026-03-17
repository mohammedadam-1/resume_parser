import os 
import sys 
import resend
from src.exception import CustomException
from src.logger import logging
from dotenv import load_dotenv
load_dotenv()

resend.api_key = os.getenv("RESEND_EMAIL_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
HR_EMAIL_RECIPIENTS = os.getenv("HR_EMAIL_RECIPIENTS", "").split(",") # get a clear understanding of this line
EMAIL_SCORE_THRESHOLD = float(os.getenv("EMAIL_SCORE_THRESHOLD"))

class EmailService:
    """Service for sending email notifications."""
    
    @staticmethod
    def notify_high_score(
        candidate_info: dict,
        job_info: dict,
        application_data: dict
    ) -> bool:
        """
        Send notification when candidate scores above threshold.
        
        Args:
            candidate_info: {name, email, phone}
            application_data: {application_id, total_score, classification}
            job_info: {job_id, job_title}
        
        Returns:
            bool: True if sent successfully
        """
        try:
        
            to_emails = [email.strip() for email in HR_EMAIL_RECIPIENTS if email.strip()] # clear understanding REQ!
            
            if not to_emails:
                logging.warning("No HR email recipients configured")
                return False
            
            subject = f"High Score Candidate Alert"
            
            html = EmailService.generate_html_template(candidate_info, application_data, job_info)
            
            params = {
                "from": EMAIL_FROM,
                "to": to_emails,
                "subject": subject,
                "html": html
            }
            
            response = resend.Emails.send(params)
            
            
            
            logging.info(f" High-score notification sent for application {application_data.get('application_id')}")
            logging.info(f" Sent to: {', '.join(to_emails)}")
                
            return True
            
        except Exception as e:
            logging.error(f" Failed to send email: {str(e)}")
            return False
        
    @staticmethod
    def generate_html_template(
        candidate_info: dict,
        application_data: dict,
        job_info: dict
    ) -> str:
        
        """Generate HTML email template"""
        
        try:
            
            score = application_data.get("total_score", 0.0) 
            classification = application_data.get('classification', 'unknown')
            
            color_map = {
                'Strong Fit': '#10B981',  # Green
                'Good Fit': '#3B82F6',       # Blue
                'Potential Fit': '#F59E0B',    # Orange
                'Not Fit': '#EF4444'         # Red
            }
            
            badge_color = color_map.get(classification, '#6B7280')
            
            html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px 8px 0 0;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                background: #ffffff;
                padding: 30px;
                border: 1px solid #e5e7eb;
                border-top: none;
            }}
            .score-badge {{
                display: inline-block;
                background: {badge_color};
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 18px;
                margin: 10px 0;
            }}
            .info-section {{
                background: #f9fafb;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #e5e7eb;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .label {{
                font-weight: 600;
                color: #6b7280;
            }}
            .value {{
                color: #111827;
            }}
            
            .cta-button {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                color: #6b7280;
                font-size: 12px;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
            }}
        </style>
    </head>
    <body>

        <div class="header">
            <h1>🌟 High-Scoring Candidate Alert</h1>
        </div>
        
        <div class="content">
            <div style="text-align: center;">
                <div class="score-badge">Score: {score}/100</div>
                <div style="color: {badge_color}; font-weight: bold; text-transform: uppercase; margin-top: 10px;">
                    {classification.replace('_', ' ')}
                </div>
            </div>
            
            <div class="info-section">
                <h2 style="margin-top: 0; color: #111827;">Candidate Information</h2>
                <div class="info-row">
                    <span class="label">Name:</span>
                    <span class="value">{candidate_info.get('name', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="label">Email:</span>
                    <span class="value">{candidate_info.get('email', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="label">Phone:</span>
                    <span class="value">{candidate_info.get('phone', 'N/A')}</span>
                </div>
            </div>
            
            <div class="info-section">
                <h2 style="margin-top: 0; color: #111827;">Position</h2>
                <div class="info-row">
                    <span class="label">Job Title:</span>
                    <span class="value">{job_info.get('job_title', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="label">Application ID:</span>
                    <span class="value" style="font-family: monospace; font-size: 12px;">{application_data.get('application_id', 'N/A')}</span>
                </div>
            </div>
            <div style="text-align: center;">
                <a href="https://dash.cloudflare.com/d53316c6fb8c6debd6a8bcbd9949d011/r2/default/buckets/candidate-resumes?prefix=resumes%2F" class="cta-button">
                    View Full Application →
                </a>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from your ATS system.</p>
                <p>Candidates scoring above {EMAIL_SCORE_THRESHOLD} trigger this alert.</p>
            </div>
        </div>
    </body>
    </html>
    """
            return html
        
        except Exception as e:
            raise CustomException(e, sys)
        
    @staticmethod
    def should_notify(score: float) -> bool:
        """Check if score exceeds notification threshold."""
        return score >= EMAIL_SCORE_THRESHOLD    

    
    
    


        
            
        

