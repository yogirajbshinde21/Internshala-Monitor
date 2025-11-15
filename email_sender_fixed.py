import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_notification(internships):
    """Send email notification for new internships"""
    
    # Get credentials from environment variables
    sender_email = os.getenv('EMAIL_ADDRESS')
    sender_password = os.getenv('EMAIL_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    # Validate credentials
    if not all([sender_email, sender_password, recipient_email]):
        print("âŒ Error: Email credentials not set in .env file")
        print("   Required: EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL")
        return False
    
    if not internships:
        print("â„¹ï¸ No internships to notify about")
        return False
    
    # Create email subject
    count = len(internships)
    subject = f"ðŸš€ {count} New Internship{'s' if count > 1 else ''} on Internshala!"
    
    # Build HTML email body with modern styling
    body_html = """
    <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                .header h1 {
                    margin: 0;
                    font-size: 28px;
                }
                .content {
                    padding: 30px;
                }
                .intro {
                    color: #333;
                    font-size: 16px;
                    margin-bottom: 25px;
                    line-height: 1.6;
                }
                .internship-card {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    transition: transform 0.2s, box-shadow 0.2s;
                    background-color: #fafafa;
                }
                .internship-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }
                .internship-title {
                    color: #667eea;
                    font-size: 20px;
                    font-weight: bold;
                    margin: 0 0 10px 0;
                }
                .info-row {
                    display: flex;
                    align-items: center;
                    margin: 8px 0;
                    color: #555;
                    font-size: 14px;
                }
                .info-label {
                    font-weight: 600;
                    margin-right: 8px;
                    color: #333;
                }
                .apply-button {
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white !important;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    margin-top: 15px;
                    font-weight: bold;
                    text-align: center;
                    transition: opacity 0.3s;
                }
                .apply-button:hover {
                    opacity: 0.9;
                }
                .footer {
                    background-color: #f8f8f8;
                    padding: 20px;
                    text-align: center;
                    color: #777;
                    font-size: 12px;
                    border-top: 1px solid #e0e0e0;
                }
                .emoji {
                    font-size: 18px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ðŸŽ‰ New Internship Opportunities!</h1>
                </div>
                <div class="content">
                    <p class="intro">
                        Great news! We found <strong>{count}</strong> new internship{plural} matching your preferences on Internshala. 
                        Apply now before the deadline!
                    </p>
    """.format(count=count, plural='s' if count > 1 else '')
    
    # Add each internship as a card
    for internship in internships:
        title = internship['title']
        company = internship['company']
        location = internship['location']
        stipend = internship['stipend']
        duration = internship['duration']
        posting_time = internship.get('posting_time', 'Recently')
        link = internship['link']
        
        body_html += """
                    <div class="internship-card">
                        <h2 class="internship-title">{title}</h2>
                        <div class="info-row">
                            <span class="info-label">ðŸ¢ Company:</span>
                            <span>{company}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">ðŸ“ Location:</span>
                            <span>{location}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">ðŸ’° Stipend:</span>
                            <span>{stipend}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">â±ï¸ Duration:</span>
                            <span>{duration}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">ðŸ• Posted:</span>
                            <span>{posting_time}</span>
                        </div>
                        <a href="{link}" class="apply-button">Apply Now â†’</a>
                    </div>
        """.format(title=title, company=company, location=location, 
                   stipend=stipend, duration=duration, posting_time=posting_time, link=link)
    
    # Close HTML
    body_html += """
                </div>
                <div class="footer">
                    <p>This is an automated notification from your Internshala Monitor.</p>
                    <p>Good luck with your applications! ðŸ€</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    # Attach HTML content
    html_part = MIMEText(body_html, 'html')
    msg.attach(html_part)
    
    # Send email
    try:
        print(f"ðŸ“§ Sending email to {recipient_email}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        print("âœ… Email notification sent successfully!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("âŒ Error: Email authentication failed")
        print("   Make sure you're using an App Password for Gmail")
        print("   Visit: https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"âŒ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"âŒ Error sending email: {e}")
        return False

if __name__ == "__main__":
    # Test with dummy data
    print("ðŸ§ª Testing email sender with dummy data...")
    test_data = [{
        'title': 'Full Stack Developer Intern',
        'company': 'Test Company Pvt. Ltd.',
        'location': 'Mumbai (Work from Home)',
        'stipend': 'â‚¹15,000/month',
        'duration': '6 months',
        'link': 'https://internshala.com/internships/detail/test',
        'found_at': '2025-11-15 18:00:00'
    }, {
        'title': 'MERN Stack Developer',
        'company': 'Tech Startup',
        'location': 'Thane',
        'stipend': 'â‚¹10,000/month',
        'duration': '3 months',
        'link': 'https://internshala.com/internships/detail/test2',
        'found_at': '2025-11-15 18:30:00'
    }]
    
    success = send_notification(test_data)
    
    if success:
        print("\nâœ… Test completed successfully!")
    else:
        print("\nâŒ Test failed. Please check your .env configuration.")

