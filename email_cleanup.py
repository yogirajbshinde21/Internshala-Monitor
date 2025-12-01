"""
Email Cleanup Module
Automatically deletes Internshala notification emails older than 2 days from Gmail.
"""

import imaplib
import email
import os
from datetime import datetime, timedelta
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

def cleanup_old_emails(days_to_keep=2):
    """
    Delete emails with subject 'New Internshala Opportunities' older than specified days.
    
    Args:
        days_to_keep (int): Number of days to keep emails before deletion (default: 2)
    """
    try:
        # Get credentials from environment
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not email_address or not email_password:
            print("❌ Email credentials not found in .env file")
            return
        
        print(f"\n🗑️  Starting email cleanup (deleting emails older than {days_to_keep} days)...")
        
        # Connect to Gmail IMAP server
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(email_address, email_password)
        
        # Select the mailbox (inbox)
        imap.select("INBOX")
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Search for emails with specific subject
        subject = "New Internshala Opportunities"
        search_criteria = f'(SUBJECT "{subject}")'
        status, messages = imap.search(None, search_criteria)
        
        if status != "OK":
            print("❌ Failed to search emails")
            imap.close()
            imap.logout()
            return
        
        email_ids = messages[0].split()
        
        if not email_ids:
            print("✅ No Internshala emails found to clean up")
            imap.close()
            imap.logout()
            return
        
        deleted_count = 0
        kept_count = 0
        
        for email_id in email_ids:
            try:
                # Fetch email data
                status, msg_data = imap.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                # Parse email
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Get email date
                date_str = msg.get("Date")
                if date_str:
                    # Parse the date (handle various formats)
                    try:
                        # Remove timezone info for comparison
                        email_date = email.utils.parsedate_to_datetime(date_str)
                        # Make it timezone-naive for comparison
                        email_date = email_date.replace(tzinfo=None)
                    except:
                        print(f"⚠️  Could not parse date for email ID {email_id.decode()}")
                        continue
                    
                    # Check if email is older than cutoff
                    if email_date < cutoff_date:
                        # Mark for deletion
                        imap.store(email_id, '+FLAGS', '\\Deleted')
                        deleted_count += 1
                        print(f"🗑️  Deleted email from {email_date.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        kept_count += 1
                        
            except Exception as e:
                print(f"⚠️  Error processing email ID {email_id.decode()}: {str(e)}")
                continue
        
        # Permanently delete marked emails
        imap.expunge()
        
        # Close connection
        imap.close()
        imap.logout()
        
        print(f"\n✅ Cleanup complete!")
        print(f"   📧 Deleted: {deleted_count} emails")
        print(f"   📬 Kept: {kept_count} emails (within {days_to_keep} days)")
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {str(e)}")
        print("   Make sure:")
        print("   1. Gmail App Password is correct")
        print("   2. IMAP is enabled in Gmail settings")
        print("   3. 2-Step Verification is enabled")
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")

if __name__ == "__main__":
    # Test the cleanup function
    cleanup_old_emails(days_to_keep=2)
