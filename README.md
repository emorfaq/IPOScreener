# IPO Screener Automation

This project contains a Python script and a GitHub Actions workflow to automatically monitor upcoming IPOs on the U.S. stock market and send an email notification for those that meet certain criteria.

## How it Works

The automation runs every day at 9:00 AM Dubai time (5:00 AM UTC) and performs the following steps:

1.  **Fetches IPO Data:** It uses the Finnhub API to get a list of IPOs scheduled for the current day.
2.  **Filters IPOs:** It identifies tickers with an offer amount (IPO price × shares) greater than USD 200 million.
3.  **Sends Email Notification:** If any IPOs meet the criteria, it sends an email to the configured recipient with a list of the ticker symbols.

## Setup

To use this automation, you need to follow these steps:

### 1. Get a Finnhub API Key

1.  Go to [Finnhub.io](https://finnhub.io/) and create a free account.
2.  Once you are logged in, you will find your API key on your dashboard.

### 2. Configure GitHub Secrets

This project uses GitHub secrets to securely store your API key and email credentials. You need to add the following secrets to your GitHub repository:

1.  `FINNHUB_API_KEY`: Your API key from Finnhub.
2.  `EMAIL_SENDER`: The email address you want to send emails from (e.g., your Gmail address).
3.  `EMAIL_PASSWORD`: The password for your email account. **Note:** If you are using Gmail, you may need to create an "App Password".
4.  `EMAIL_RECIPIENT`: The email address you want to send the notifications to.
5.  `SMTP_SERVER`: The SMTP server for your email provider (e.g., `smtp.gmail.com` for Gmail). This is optional and defaults to `smtp.gmail.com`.
6.  `SMTP_PORT`: The SMTP port for your email provider (e.g., `587` for Gmail). This is optional and defaults to `587`.

To add secrets to your repository:

1.  Go to your repository on GitHub.
2.  Click on the "Settings" tab.
3.  In the left sidebar, click on "Secrets and variables" > "Actions".
4.  Click the "New repository secret" button for each secret listed above and paste the corresponding value.

## Verification

To verify that the automation is working correctly, you can manually trigger the workflow:

1.  Go to the "Actions" tab of your repository.
2.  In the left sidebar, click on the "IPO Screener" workflow.
3.  Click the "Run workflow" dropdown button on the right side.
4.  Click the green "Run workflow" button.

This will run the automation immediately. You can check the workflow logs to see the output of the script and whether an email was sent. If everything is configured correctly, you should receive an email if there are any IPOs that meet the criteria on the day you run the test.
