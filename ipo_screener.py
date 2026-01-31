import os
import requests
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# --- Configuration ---
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = 587
OFFER_AMOUNT_THRESHOLD = 200_000_000


def get_ipos(api_key, todays_date):
    """Fetches upcoming IPOs from Finnhub."""
    if not api_key:
        print("FINNHUB_API_KEY not set")
        return None
    
    today = todays_date
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = f"https://finnhub.io/api/v1/calendar/ipo?from={start_date}&to={end_date}&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched {len(data.get('ipoCalendar', []))} IPOs")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO data: {e}")
        return None

def send_email(subject, body):
    """Send properly formatted MIME email (fixes Unicode error)."""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("Email credentials incomplete. Skipping email.")
        return False

    # Create MIME message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject
    
    # Body as UTF-8 text
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)  # Use send_message() for MIME
        print("✅ Email sent successfully.")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Auth failed: {e}")
        print("💡 Use Gmail App Password: myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


def main():
    """Main function to run the IPO screener."""
    if not FINNHUB_API_KEY:
        print("Set FINNHUB_API_KEY environment variable")
        return


    
    todays_date = date.today()


    ipo_data = get_ipos(FINNHUB_API_KEY, todays_date)
    if not ipo_data or not ipo_data.get("ipoCalendar"):
        print("No IPOs found for today.")
        return

    filtered_ipos = []
    for ipo in ipo_data["ipoCalendar"]:
        price_str = ipo.get("price")
        if price_str is None:
            continue
        price_range = price_str.split("-")
        try:
            price = float(price_range[-1])
            shares = ipo.get("numberOfShares", 0) or 0
            offer_amount = price * shares
            if offer_amount > OFFER_AMOUNT_THRESHOLD:
                filtered_ipos.append(ipo)
        except (ValueError, IndexError, TypeError):
            continue

    if filtered_ipos:
        subject = f"High-Value IPOs >${OFFER_AMOUNT_THRESHOLD/1_000_000:.0f}M ({len(filtered_ipos)} found for date {todays_date} )"
        body = f"Offer amount = IPO price × shares\n\n"
        for ipo in filtered_ipos:
            symbol = ipo.get('symbol', 'N/A')
            name = ipo.get('name', 'Unknown')
            shares = ipo.get('numberOfShares', 0)
            price = ipo.get('price', 'N/A')
            body += f"- {symbol}: {name} ({shares:,} shares @ {price})\n"
        
        print(f"Found {len(filtered_ipos)} qualifying IPOs")
        print(body)
        send_email(subject, body)
    else:
        print("No IPOs meet criteria (> $200M offer)")

if __name__ == "__main__":
    main()
