"""
Wise API Configuration Module
Centralized configuration for URLs, tokens, headers, and currencies.
"""

import os
from dotenv import load_dotenv

# Step 1 - Load environment variables
load_dotenv()

# Step 2 - API Token
TOKEN_WISE = os.getenv("TOKEN_WISE")

# Step 3 - Base URL
BASE_URL = "https://api.wise.com"  # Production API

# Step 4 - Request Headers
HEADERS = {
    "Authorization": f"Bearer {TOKEN_WISE}",
    "Content-Type": "application/json"
}

# Step 5 - API Endpoint URLs
# Step 5.1 - Profile endpoints
ENDPOINT_PROFILES = f"{BASE_URL}/v1/profiles"
ENDPOINT_CURRENT_USER = f"{BASE_URL}/v1/me"
ENDPOINT_BALANCES = f"{BASE_URL}/v4/profiles/{{profile_id}}/balances"  # .format(profile_id=...)

# Step 5.2 - Account endpoints
ENDPOINT_ACCOUNTS = f"{BASE_URL}/v2/accounts"
ENDPOINT_ACCOUNTS_CREATE = f"{BASE_URL}/v1/accounts"
ENDPOINT_ACCOUNT_REQUIREMENTS = f"{BASE_URL}/v1/account-requirements"

# Step 5.3 - Quote endpoints
ENDPOINT_QUOTES = f"{BASE_URL}/v3/profiles/{{profile_id}}/quotes"  # .format(profile_id=...)
ENDPOINT_QUOTE_UPDATE = f"{BASE_URL}/v3/profiles/{{profile_id}}/quotes/{{quote_id}}"  # .format(profile_id=..., quote_id=...)

# Step 5.4 - Transfer endpoints
ENDPOINT_TRANSFERS = f"{BASE_URL}/v1/transfers"
ENDPOINT_TRANSFER_STATUS = f"{BASE_URL}/v1/transfers/{{transfer_id}}"  # .format(transfer_id=...)
ENDPOINT_TRANSFER_CANCEL = f"{BASE_URL}/v1/transfers/{{transfer_id}}/cancel"  # .format(transfer_id=...)
ENDPOINT_TRANSFER_FUND = f"{BASE_URL}/v3/profiles/{{profile_id}}/transfers/{{transfer_id}}/payments"  # .format(...)
ENDPOINT_DELIVERY_ESTIMATE = f"{BASE_URL}/v1/delivery-estimates/{{transfer_id}}"  # .format(transfer_id=...)

# Step 6 - Supported currencies for account fetching
SUPPORTED_CURRENCIES = ["EUR", "USD", "GBP", "INR", "AUD", "CAD", "CHF", "PLN", "SEK", "NOK", "DKK"]

# Step 6 - UI Currency Options
BASE_CURRENCY_OPTIONS = ["EUR", "GBP", "USD", "CHF", "INR"]   # For sidebar base currency selector
ACCOUNT_CURRENCY_OPTIONS = ["EUR", "USD", "GBP", "CHF", "PLN", "INR"]  # For new account creation
COUNTRY_CODE_OPTIONS = ["NL", "DE", "BE", "FR", "GB", "US", "CH"]  # For new account country selection
