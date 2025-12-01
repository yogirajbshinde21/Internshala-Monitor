"""
Notification Manager - Smart Email Delivery System
Implements anti-clutter strategies for production-ready startup use
"""

import json
import os
from datetime import datetime, time
from pathlib import Path

class NotificationManager:
    """Manages notification delivery with anti-clutter strategies"""
    
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.notification_settings = self.config.get('notification_settings', {})
        self.daily_log_path = Path("data/daily_email_log.json")
        self.pending_batch_path = Path("data/pending_batch.json")
        
    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            return {}
    
    def should_send_notification(self, new_internships_count):
        """
        Determine if notification should be sent based on multiple factors
        
        Returns: (should_send: bool, reason: str)
        """
        # Check 1: Minimum internship threshold
        min_threshold = self.notification_settings.get('min_internships_to_notify', 1)
        if new_internships_count < min_threshold:
            return False, f"Only {new_internships_count} internship(s) found (minimum: {min_threshold})"
        
        # Check 2: Quiet hours
        if self._is_quiet_hours():
            return False, "Currently in quiet hours (notifications paused)"
        
        # Check 3: Daily email limit
        if self._exceeded_daily_limit():
            return False, "Daily email limit reached"
        
        # Check 4: Digest mode
        if self.notification_settings.get('digest_mode', False):
            return False, "Digest mode enabled (batching for later)"
        
        return True, "Ready to send"
    
    def _is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        quiet_hours = self.notification_settings.get('quiet_hours', {})
        
        if not quiet_hours.get('enabled', False):
            return False
        
        now = datetime.now()
        current_hour = now.hour
        
        start_hour = quiet_hours.get('start_hour', 22)  # 10 PM
        end_hour = quiet_hours.get('end_hour', 8)      # 8 AM
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start_hour > end_hour:
            return current_hour >= start_hour or current_hour < end_hour
        else:
            return start_hour <= current_hour < end_hour
    
    def _exceeded_daily_limit(self):
        """Check if daily email limit has been exceeded"""
        max_emails = self.notification_settings.get('max_emails_per_day', 12)
        
        if max_emails == 0:  # Unlimited
            return False
        
        today_count = self._get_today_email_count()
        return today_count >= max_emails
    
    def _get_today_email_count(self):
        """Get number of emails sent today"""
        try:
            if not self.daily_log_path.exists():
                return 0
            
            with open(self.daily_log_path, 'r') as f:
                log = json.load(f)
            
            today = datetime.now().strftime('%Y-%m-%d')
            return log.get(today, 0)
        except:
            return 0
    
    def record_email_sent(self):
        """Record that an email was sent today"""
        try:
            # Create data directory if it doesn't exist
            self.daily_log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing log
            if self.daily_log_path.exists():
                with open(self.daily_log_path, 'r') as f:
                    log = json.load(f)
            else:
                log = {}
            
            # Update today's count
            today = datetime.now().strftime('%Y-%m-%d')
            log[today] = log.get(today, 0) + 1
            
            # Clean up old dates (keep last 7 days)
            cutoff_date = (datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            log = {k: v for k, v in log.items() if k >= cutoff_date}
            
            # Save log
            with open(self.daily_log_path, 'w') as f:
                json.dump(log, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Could not record email: {e}")
    
    def add_to_batch(self, internships):
        """Add internships to pending batch for digest mode"""
        try:
            self.pending_batch_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing batch
            if self.pending_batch_path.exists():
                with open(self.pending_batch_path, 'r') as f:
                    batch = json.load(f)
            else:
                batch = {
                    'internships': [],
                    'created_at': datetime.now().isoformat()
                }
            
            # Add new internships (avoid duplicates)
            existing_urls = {item['apply_link'] for item in batch['internships']}
            new_items = [item for item in internships if item['apply_link'] not in existing_urls]
            batch['internships'].extend(new_items)
            batch['updated_at'] = datetime.now().isoformat()
            
            # Save batch
            with open(self.pending_batch_path, 'w') as f:
                json.dump(batch, f, indent=2)
            
            return len(new_items)
            
        except Exception as e:
            print(f"⚠️  Could not add to batch: {e}")
            return 0
    
    def get_pending_batch(self):
        """Get all pending internships from batch"""
        try:
            if not self.pending_batch_path.exists():
                return []
            
            with open(self.pending_batch_path, 'r') as f:
                batch = json.load(f)
            
            return batch.get('internships', [])
        except:
            return []
    
    def clear_batch(self):
        """Clear the pending batch after sending"""
        try:
            if self.pending_batch_path.exists():
                self.pending_batch_path.unlink()
        except Exception as e:
            print(f"⚠️  Could not clear batch: {e}")
    
    def get_next_notification_time(self):
        """Calculate when the next notification can be sent"""
        if self._is_quiet_hours():
            quiet_hours = self.notification_settings.get('quiet_hours', {})
            end_hour = quiet_hours.get('end_hour', 8)
            
            now = datetime.now()
            next_time = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
            
            # If end_hour is earlier today, it's tomorrow
            if next_time <= now:
                next_time += datetime.timedelta(days=1)
            
            return next_time
        
        if self._exceeded_daily_limit():
            # Next notification tomorrow
            tomorrow = datetime.now() + datetime.timedelta(days=1)
            return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return None
    
    def get_check_interval_hours(self):
        """Get configured check interval in hours"""
        return self.notification_settings.get('check_interval_hours', 2)
    
    def print_status(self):
        """Print current notification manager status"""
        print("\n📊 Notification Settings:")
        print(f"   ⏱️  Check interval: Every {self.get_check_interval_hours()} hour(s)")
        print(f"   📧 Min internships to notify: {self.notification_settings.get('min_internships_to_notify', 1)}")
        print(f"   📬 Max emails per day: {self.notification_settings.get('max_emails_per_day', 12)}")
        print(f"   📮 Emails sent today: {self._get_today_email_count()}")
        
        quiet_hours = self.notification_settings.get('quiet_hours', {})
        if quiet_hours.get('enabled', False):
            print(f"   🌙 Quiet hours: {quiet_hours.get('start_hour', 22)}:00 - {quiet_hours.get('end_hour', 8)}:00")
            print(f"   🔕 In quiet hours: {'Yes' if self._is_quiet_hours() else 'No'}")
        
        if self.notification_settings.get('digest_mode', False):
            pending = len(self.get_pending_batch())
            print(f"   📦 Digest mode: Enabled ({pending} pending internships)")


if __name__ == "__main__":
    # Test the notification manager
    nm = NotificationManager()
    nm.print_status()
    
    # Test decision
    should_send, reason = nm.should_send_notification(5)
    print(f"\n🤔 Should send notification for 5 internships?")
    print(f"   {'✅ Yes' if should_send else '❌ No'}: {reason}")
