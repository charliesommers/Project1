#!/bin/bash
#
# Quick setup script for daily picks automation at 5:30 AM Central Time
#

echo "🏀 CBB Picks Automation Setup"
echo "================================"
echo ""

# Create logs directory
echo "Creating logs directory..."
mkdir -p /home/user/Project1/logs
echo "✓ Created /home/user/Project1/logs"
echo ""

# Check if .env exists
if [ ! -f /home/user/Project1/.env ]; then
    echo "❌ Error: .env file not found"
    echo ""
    echo "Please create /home/user/Project1/.env with:"
    echo ""
    echo "ODDS_API_KEY=32a952b95065c6b8c74f1e72ac125602"
    echo "EMAIL_FROM=your@gmail.com"
    echo "EMAIL_TO=your@email.com"
    echo "EMAIL_PASSWORD=your_app_password"
    echo ""
    exit 1
fi

# Check if email is configured
if ! grep -q "EMAIL_FROM" /home/user/Project1/.env; then
    echo "⚠️  Warning: Email not configured in .env"
    echo ""
    echo "Add these lines to .env:"
    echo "EMAIL_FROM=your@gmail.com"
    echo "EMAIL_TO=your@email.com"
    echo "EMAIL_PASSWORD=your_app_password"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Test email (optional)
echo "Would you like to test email now?"
read -p "Send test email? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Sending test email..."
    cd /home/user/Project1
    python3 email_picks.py
    echo ""
fi

# Add to crontab
echo "Setting up daily automation..."
echo ""
echo "This will run at 5:30 AM Central Time (11:30 AM UTC in winter, 10:30 AM UTC in summer)"
echo ""

# Create cron job (CST - winter time)
CRON_CMD_WINTER="30 11 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1"

# Create cron job (CDT - summer time)
CRON_CMD_SUMMER="30 10 * * * cd /home/user/Project1 && /usr/bin/python3 email_picks.py >> /home/user/Project1/logs/email.log 2>&1"

echo "Choose your timezone setting:"
echo ""
echo "1) CST - Central Standard Time (Winter) - Use Nov-Mar"
echo "2) CDT - Central Daylight Time (Summer) - Use Mar-Nov"
echo "3) Manual - I'll set it myself"
echo ""
read -p "Enter choice (1/2/3): " -n 1 -r
echo ""

case $REPLY in
    1)
        # Add CST cron job
        (crontab -l 2>/dev/null | grep -v "email_picks.py"; echo "$CRON_CMD_WINTER") | crontab -
        echo "✓ Added cron job for CST (5:30 AM = 11:30 AM UTC)"
        echo ""
        echo "NOTE: In March when DST starts, run this script again and choose option 2"
        ;;
    2)
        # Add CDT cron job
        (crontab -l 2>/dev/null | grep -v "email_picks.py"; echo "$CRON_CMD_SUMMER") | crontab -
        echo "✓ Added cron job for CDT (5:30 AM = 10:30 AM UTC)"
        echo ""
        echo "NOTE: In November when DST ends, run this script again and choose option 1"
        ;;
    3)
        echo "Skipping automatic cron setup"
        echo ""
        echo "To add manually, run: crontab -e"
        echo ""
        echo "For CST (Winter): $CRON_CMD_WINTER"
        echo "For CDT (Summer): $CRON_CMD_SUMMER"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Setup complete!"
echo ""
echo "Your picks will be emailed daily at 5:30 AM Central Time"
echo ""
echo "To check cron job: crontab -l"
echo "To view logs: tail -f /home/user/Project1/logs/email.log"
echo ""
echo "🏀 Good luck!"
