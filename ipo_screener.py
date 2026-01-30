import os
import requests
import smtplib
from datetime import date, timedelta

# --- Configuration ---
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = 587
OFFER_AMOUNT_THRESHOLD = 200_000_000

# --- Finnhub API ---
def get_ipos(api_key):
    """Fetches upcoming IPOs from Finnhub."""
    today = date.today()
    # Finnhub API takes a start and end date. We are only interested in today's IPOs.
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = f"https://finnhub.io/api/v1/calendar/ipo?from={start_date}&to={end_date}&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IPO data: {e}")
        return None

# --- Email ---
def send_email(subject, body):
    """Sends an email with the specified subject and body."""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("Email credentials not fully configured. Skipping email.")
        return

    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, message)
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

# --- Main Logic ---
def main():
    """Main function to run the IPO screener."""
    if not FINNHUB_API_KEY:
        print("FINNHUB_API_KEY environment variable not set.")
        return

    ipo_data = get_ipos(FINNHUB_API_KEY)

    if not ipo_data or not ipo_data.get("ipoCalendar"):
        print("No IPOs found for today.")
        return

    filtered_ipos = []
    for ipo in ipo_data["ipoCalendar"]:
        price_range = ipo.get("price", "0-0").split("-")
        try:
            # Use the higher end of the price range for calculation
            price = float(price_range[-1])
            shares = ipo.get("numberOfShares", 0)
            offer_amount = price * shares

            if offer_amount > OFFER_AMOUNT_THRESHOLD:
                filtered_ipos.append(ipo)
        except (ValueError, IndexError):
            # Ignore IPOs with malformed price data
            continue
            
    if filtered_ipos:
        subject = "High-Value IPOs for Today"
        body = "The following IPOs have an offer amount greater than $200 million:\n\n"
        for ipo in filtered_ipos:
            body += f"- {ipo['symbol']}\n"
        
        print(body)
        send_email(subject, body)
    else:
        print("No IPOs found today that meet the criteria.")

if __name__ == "__main__":
    main()
