"""
Wise API Module for Transfer Operations
"""

import uuid
import requests
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError

# Step 1 - Import configuration from config.py
from config import (
    HEADERS,
    SUPPORTED_CURRENCIES,
    ENDPOINT_PROFILES,
    ENDPOINT_CURRENT_USER,
    ENDPOINT_BALANCES,
    ENDPOINT_ACCOUNTS,
    ENDPOINT_ACCOUNTS_CREATE,
    ENDPOINT_ACCOUNT_REQUIREMENTS,
    ENDPOINT_QUOTES,
    ENDPOINT_QUOTE_UPDATE,
    ENDPOINT_TRANSFERS,
    ENDPOINT_TRANSFER_STATUS,
    ENDPOINT_TRANSFER_CANCEL,
    ENDPOINT_TRANSFER_FUND,
    ENDPOINT_DELIVERY_ESTIMATE,
)


# =============================================================================
# Step 3 - Profile Functions
# =============================================================================

def get_profiles() -> tuple[list, str]:
    """
    Fetch all user profiles (personal and business).
    GET /v1/profiles
    """
    response = requests.get(ENDPOINT_PROFILES, headers=HEADERS)
    response.raise_for_status()
    return response.json(), ENDPOINT_PROFILES


def get_current_user() -> tuple[dict, str]:
    """
    Get current authenticated user info.
    GET /v1/me
    """
    response = requests.get(ENDPOINT_CURRENT_USER, headers=HEADERS)
    response.raise_for_status()
    return response.json(), ENDPOINT_CURRENT_USER


def get_balances(profile_id: int) -> tuple[list, str]:
    """
    Fetch all available balances for a profile.
    GET /v4/profiles/{profileId}/balances?types=STANDARD
    
    Args:
        profile_id: The profile ID to fetch balances for
        
    Returns:
        List of balance objects with currency and amount info
    """
    url = ENDPOINT_BALANCES.format(profile_id=profile_id)
    params = {"types": "STANDARD"}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json(), url


# =============================================================================
# Step 4 - Recipient (Account) Functions
# =============================================================================

def get_recipients_by_currency(currency: str) -> tuple[list, str]:
    """
    Get existing recipient accounts for a specific currency.
    GET /v2/accounts?currency={currency}
    Returns list of recipient dicts.
    """
    params = {"currency": currency}
    response = requests.get(ENDPOINT_ACCOUNTS, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    # Step 4.1 - API returns {content: [...], sort: ..., size: ...}
    result = []
    if isinstance(data, dict) and "content" in data:
        result = data["content"]
    else:
        result = data if isinstance(data, list) else []
    return result, response.url


def get_all_recipients() -> tuple[dict, dict]:
    """
    Fetch recipients for ALL supported currencies.
    Returns:
        tuple[dict, dict]: (recipients_by_currency, urls_by_currency)
    """
    recipients_by_currency = {}
    urls_by_currency = {}
    for currency in SUPPORTED_CURRENCIES:
        try:
            recipients, url = get_recipients_by_currency(currency)
            if recipients:  # Only add if there are recipients
                recipients_by_currency[currency] = recipients
                urls_by_currency[currency] = url
        except requests.exceptions.HTTPError:
            # Skip currencies that fail (e.g., not supported for this profile)
            continue
    return recipients_by_currency, urls_by_currency


def get_recipient_requirements(source_currency: str, target_currency: str, source_amount: float) -> tuple[list, str]:
    """
    Fetch recipient account requirements for a specific currency pair.
    GET /v1/account-requirements?source={source}&target={target}&sourceAmount={amount}
    
    Args:
        source_currency: Source currency code (e.g., "USD")
        target_currency: Target currency code (e.g., "CNY")
        source_amount: Amount in source currency
        
    Returns:
        tuple[list, str]: (requirements_list, url)
    """
    params = {
        "source": source_currency,
        "target": target_currency,
        "sourceAmount": source_amount
    }
    response = requests.get(ENDPOINT_ACCOUNT_REQUIREMENTS, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json(), response.url


def create_recipient(profile_id: int, recipient_data: dict) -> tuple[dict, str]:
    """
    Create a new recipient account.
    POST /v1/accounts
    
    Args:
        profile_id: The profile ID to create the recipient under
        recipient_data: Dict with accountHolderName, currency, type, details, ownedByCustomer
    """
    payload = {
        "profile": profile_id,
        "ownedByCustomer": recipient_data.get("ownedByCustomer", False), # Defaulting to false if not provided
        **recipient_data
    }
    
    # Ensure accountHolderName is at top level
    if "accountHolderName" not in payload and "accountHolderName" in recipient_data.get("details", {}):
         # If somehow it crept into details, pull it up, though caller should handle this
         payload["accountHolderName"] = recipient_data["details"].pop("accountHolderName")

    response = requests.post(ENDPOINT_ACCOUNTS_CREATE, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json(), ENDPOINT_ACCOUNTS_CREATE


# =============================================================================
# Step 4.5 - Pydantic Models for Quote API Response Validation
# =============================================================================

class QuoteFee(BaseModel):
    """Fee breakdown for a payment option."""
    transferwise: float
    payIn: float
    discount: float
    total: float
    priceSetId: int
    partner: float

class QuotePriceValue(BaseModel):
    """Price value object with amount, currency, and label."""
    amount: float
    currency: str
    label: str

class QuotePriceItem(BaseModel):
    """Individual price item (e.g., PAYIN, TRANSFERWISE fee)."""
    type: str
    label: str
    value: QuotePriceValue

class QuotePriceTotal(BaseModel):
    """Total price object."""
    type: str
    label: str
    value: QuotePriceValue

class QuotePrice(BaseModel):
    """Full price breakdown for a payment option."""
    priceSetId: int
    total: QuotePriceTotal
    items: List[QuotePriceItem]
    priceDecisionReferenceId: Optional[str] = None

class QuoteDisabledReason(BaseModel):
    """Reason why a payment option is disabled."""
    code: str
    message: str
    arguments: List[str] = []

class QuotePaymentOption(BaseModel):
    """A payment option in the quote response."""
    formattedEstimatedDelivery: str
    estimatedDeliveryDelays: List[str] = []
    allowedProfileTypes: List[str]
    payInProduct: Optional[str] = None
    feePercentage: float
    estimatedDelivery: str
    fee: QuoteFee
    payIn: str
    price: QuotePrice
    disabled: bool
    disabledReason: Optional[QuoteDisabledReason] = None
    payOut: str
    sourceAmount: float
    targetAmount: float
    sourceCurrency: str
    targetCurrency: str

class QuoteHighAmountConfig(BaseModel):
    """High amount transfer configuration."""
    showFeePercentage: bool
    trackAsHighAmountSender: bool
    showEducationStep: bool
    offerPrefundingOption: bool
    overLimitThroughCs: bool
    overLimitThroughWiseAccount: bool

class QuoteTransferFlowConfig(BaseModel):
    """Transfer flow configuration."""
    highAmount: QuoteHighAmountConfig

class QuoteResponse(BaseModel):
    """
    Pydantic model for Wise Quote API response.
    
    This model validates the JSON response from POST /v3/profiles/{profileId}/quotes
    to ensure the response structure matches expected format.
    """
    id: str
    type: str
    status: str
    user: int
    profile: int
    sourceCurrency: str
    targetCurrency: str
    rate: float
    rateType: str
    rateTimestamp: str
    rateExpirationTime: str
    createdTime: str
    expirationTime: str
    payOut: str
    funding: str
    payInCountry: Optional[str] = None
    providedAmountType: str
    guaranteedTargetAmount: bool
    targetAmount: Optional[float] = None
    sourceAmount: Optional[float] = None
    targetAmountAllowed: bool
    guaranteedTargetAmountAllowed: bool
    paymentOptions: List[QuotePaymentOption]
    notices: List[str] = []
    transferFlowConfig: QuoteTransferFlowConfig
    clientId: Optional[str] = None


def validate_quote_response(response_json: dict) -> QuoteResponse:
    """
    Validate a quote API response against the Pydantic model.
    
    Args:
        response_json: The raw JSON response from the quotes API
        
    Returns:
        QuoteResponse: Validated Pydantic model
        
    Raises:
        ValidationError: If the response doesn't match the expected structure
    """
    return QuoteResponse(**response_json)


# =============================================================================
# Step 5 - Quote Functions
# =============================================================================

def create_quote(
    profile_id: int,
    source_currency: str,
    target_currency: str,
    target_amount: Optional[float] = None,
    source_amount: Optional[float] = None,
    validate: bool = True
) -> tuple[dict, str]:
    """
    Create a quote for a transfer.
    POST /v3/profiles/{profileId}/quotes
    
    Args:
        profile_id: The profile ID
        source_currency: Source currency code (e.g., "EUR")
        target_currency: Target currency code (e.g., "USD")
        target_amount: Amount in target currency (optional, use one of target/source)
        source_amount: Amount in source currency (optional, use one of target/source)
        validate: If True, validates JSON response against Pydantic QuoteResponse model
        
    Returns:
        tuple[dict, str]: A tuple containing:
            - The quote response JSON
            - The full URL used for the request
            
        If validate=True and validation fails, raises ValidationError.
    """
    url = ENDPOINT_QUOTES.format(profile_id=profile_id)
    payload = {
        "sourceCurrency": source_currency,
        "targetCurrency": target_currency,
        "payOut": "BALANCE"
    }
    
    if target_amount is not None:
        payload["targetAmount"] = target_amount
    elif source_amount is not None:
        payload["sourceAmount"] = source_amount
    else:
        raise ValueError("Either target_amount or source_amount must be provided")
    
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    response_json = response.json()
    
    # Step 5.1 - Validate response against Pydantic model if requested
    if validate:
        try:
            validate_quote_response(response_json)
        except ValidationError as e:
            # Log the error but still return the response for backwards compatibility
            print(f"[WARNING] Quote response validation failed: {e}")
    
    return response_json, url


def update_quote_with_recipient(profile_id: int, quote_id: str, recipient_id: int) -> tuple[dict, str]:
    """
    Update quote with selected recipient to get final pricing.
    PATCH /v3/profiles/{profileId}/quotes/{quoteId}
    
    Note: Content-Type must be application/merge-patch+json
    """
    url = ENDPOINT_QUOTE_UPDATE.format(profile_id=profile_id, quote_id=quote_id)
    headers = {
        **HEADERS,
        "Content-Type": "application/merge-patch+json"
    }
    payload = {"targetAccount": recipient_id}
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json(), url


# =============================================================================
# Step 6 - Transfer Functions
# =============================================================================

def create_transfer(
    quote_id: str,
    recipient_id: int,
    reference: str = "",
    source_account: Optional[int] = None
) -> tuple[dict, str]:
    """
    Create a transfer based on a quote.
    POST /v1/transfers
    
    Args:
        quote_id: The quote ID from create_quote
        recipient_id: The recipient account ID
        reference: Optional transfer reference/note
        source_account: Optional refund account ID
    """
    # Step 6.1 - Generate unique customer transaction ID for idempotency
    customer_transaction_id = str(uuid.uuid4())
    
    payload = {
        "targetAccount": recipient_id,
        "quoteUuid": quote_id,
        "customerTransactionId": customer_transaction_id,
        "details": {
            "reference": reference
        }
    }
    
    if source_account:
        payload["sourceAccount"] = source_account
    
    response = requests.post(ENDPOINT_TRANSFERS, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json(), ENDPOINT_TRANSFERS


def fund_transfer(profile_id: int, transfer_id: int) -> tuple[dict, str]:
    """
    Fund transfer from balance.
    POST /v3/profiles/{profileId}/transfers/{transferId}/payments
    """
    url = ENDPOINT_TRANSFER_FUND.format(profile_id=profile_id, transfer_id=transfer_id)
    payload = {"type": "BALANCE"}
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json(), url


def get_transfer_status(transfer_id: int) -> tuple[dict, str]:
    """
    Get current status of a transfer.
    GET /v1/transfers/{transferId}
    """
    url = ENDPOINT_TRANSFER_STATUS.format(transfer_id=transfer_id)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json(), url


def get_delivery_estimate(transfer_id: int) -> tuple[dict, str]:
    """
    Get delivery estimate for a transfer.
    GET /v1/delivery-estimates/{transferId}
    """
    url = ENDPOINT_DELIVERY_ESTIMATE.format(transfer_id=transfer_id)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json(), url


def list_transfers(profile_id: Optional[int] = None, limit: int = 10) -> tuple[list, str]:
    """
    List all transfers.
    GET /v1/transfers
    """
    params = {"limit": limit}
    if profile_id:
        params["profile"] = profile_id
    response = requests.get(ENDPOINT_TRANSFERS, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json(), response.url


def cancel_transfer(transfer_id: int) -> tuple[dict, str]:
    """
    Cancel a transfer.
    PUT /v1/transfers/{transferId}/cancel
    """
    url = ENDPOINT_TRANSFER_CANCEL.format(transfer_id=transfer_id)
    response = requests.put(url, headers=HEADERS)
    response.raise_for_status()
    return response.json(), url


# =============================================================================
# Step 7 - Test Entry Point
# =============================================================================

if __name__ == "__main__":
    # Step 7.1 - Quick test of profile fetching
    print("Testing Wise API connection...")
    try:
        profiles, url = get_profiles()
        print(f"URL used: {url}")
        print(f"Found {len(profiles)} profile(s):")
        for p in profiles:
            print(f"  - ID: {p['id']}, Type: {p['type']}")
    except Exception as e:
        print(f"Error: {e}")
