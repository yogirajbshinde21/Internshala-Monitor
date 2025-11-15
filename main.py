from scraper import scrape_internshala, load_config
from email_sender import send_notification
import sys

def main():
    """Main orchestrator for the Internshala monitor system"""
    print("=" * 60)
    print("🔍 INTERNSHALA INTERNSHIP MONITOR")
    print("=" * 60)
    print()
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration. Exiting.")
        sys.exit(1)
    
    print(f"📋 Configuration loaded:")
    print(f"   Locations: {', '.join(config.get('locations', [])[:5])}...")
    print(f"   Min Stipend: ₹{config.get('min_stipend', 0)}")
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
        print("📧 Sending email notification...")
        
        success = send_notification(new_internships)
        
        if success:
            print()
            print("=" * 60)
            print("✅ ALL DONE! Email notification sent successfully.")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("⚠️ Warning: Internships found but email failed to send.")
            print("   Check your .env configuration.")
            print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("✅ ALL CAUGHT UP!")
        print("   No new matching internships at this time.")
        print("=" * 60)
    
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
