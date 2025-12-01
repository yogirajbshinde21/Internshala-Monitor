from scraper import scrape_internshala, load_config
from email_sender import send_notification
from email_cleanup import cleanup_old_emails
from notification_manager import NotificationManager
import sys
from datetime import datetime

def main():
    """Main orchestrator for the Internshala monitor system"""
    print("=" * 60)
    print("🔍 INTERNSHALA INTERNSHIP MONITOR")
    print("=" * 60)
    print()
    
    # Initialize notification manager
    nm = NotificationManager()
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration. Exiting.")
        sys.exit(1)
    
    print(f"📋 Configuration loaded:")
    print(f"   Locations: {', '.join(config.get('locations', [])[:5])}...")
    print(f"   Min Stipend: ₹{config.get('min_stipend', 0)}")
    
    # Show notification settings
    nm.print_status()
    print()
    
    # Scrape for new internships
    print("🔍 Starting internship search...")
    new_internships = scrape_internshala()
    
    # Send notification if new internships found
    if new_internships:
        print()
        print("=" * 60)
        print(f"✅ SUCCESS: Found {len(new_internships)} new internship(s)")
        print("=" * 60)
        print()
        
        # Display summary
        print("📊 Summary of new internships:")
        for idx, internship in enumerate(new_internships, 1):
            print(f"{idx}. {internship['title']} at {internship['company']}")
            print(f"   💰 {internship['stipend']} | 📍 {internship['location']}")
        
        print()
        
        # Check if notification should be sent (anti-clutter logic)
        should_send, reason = nm.should_send_notification(len(new_internships))
        
        if should_send:
            print("📧 Sending email notification...")
            success = send_notification(new_internships)
            
            if success:
                print()
                print("=" * 60)
                print("✅ ALL DONE! Email notification sent successfully.")
                print("=" * 60)
                
                # Record email sent
                nm.record_email_sent()
                
                # Clean up old emails after successful send
                print()
                cleanup_old_emails(days_to_keep=config.get('email_cleanup', {}).get('retention_days', 2))
            else:
                print()
                print("=" * 60)
                print("⚠️ Warning: Internships found but email failed to send.")
                print("   Check your .env configuration.")
                print("=" * 60)
        else:
            # Don't send email - add to batch or skip
            print(f"🔕 Email not sent: {reason}")
            
            if nm.notification_settings.get('batch_notifications', False):
                added = nm.add_to_batch(new_internships)
                print(f"📦 Added {added} internships to batch for next digest email")
            
            next_time = nm.get_next_notification_time()
            if next_time:
                print(f"⏰ Next notification possible at: {next_time.strftime('%Y-%m-%d %H:%M')}")
            
            # Still run cleanup
            print()
            cleanup_old_emails(days_to_keep=config.get('email_cleanup', {}).get('retention_days', 2))
    else:
        print()
        print("=" * 60)
        print("✅ ALL CAUGHT UP!")
        print("   No new matching internships at this time.")
        print("=" * 60)
        
        # Check if there are batched internships to send
        batched = nm.get_pending_batch()
        if batched and len(batched) > 0:
            print()
            print(f"📦 Found {len(batched)} internships in pending batch")
            
            # Check if we can send digest now
            should_send, reason = nm.should_send_notification(len(batched))
            if should_send:
                print("📧 Sending digest email with batched internships...")
                success = send_notification(batched)
                
                if success:
                    print("✅ Digest email sent successfully!")
                    nm.record_email_sent()
                    nm.clear_batch()
                else:
                    print("⚠️ Failed to send digest email")
            else:
                print(f"🔕 Digest not sent yet: {reason}")
        
        # Still run cleanup even when no new internships found
        print()
        cleanup_old_emails(days_to_keep=config.get('email_cleanup', {}).get('retention_days', 2))
    
    print()
    print("Monitor run completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
