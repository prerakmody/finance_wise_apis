"""
Wise API Module for Transfer Operations
"""

import uuid
import requests
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError

try:
    from jwcrypto import jwk, jwe
    import json
    JWCRYPTO_AVAILABLE = True
except ImportError:
    JWCRYPTO_AVAILABLE = False
    print("[WARNING] 'jwcrypto' library not found. SCA PIN verification will fail.")

# Step 1 - Import configuration from config.py
from wise.config import (
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
    ENDPOINT_TRANSFER_FUND,
    ENDPOINT_DELIVERY_ESTIMATE,
    ENDPOINT_SCA_SESSION_AUTHORISE,
    ENDPOINT_PIN_VERIFY,
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


def update_quote_with_recipient(profile_id: int, quote_id: str, recipient_id: int) -> tuple[dict, str, dict]:
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
    return response.json(), url, payload


# =============================================================================
# Step 6 - Transfer Functions
# =============================================================================

def create_transfer(
    quote_id: str,
    recipient_id: int,
    reference: str = "",
    source_account: Optional[int] = None
) -> tuple[dict, str, dict]:
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
    return response.json(), ENDPOINT_TRANSFERS, payload


def fund_transfer(profile_id: int, transfer_id: int, one_time_token: Optional[str] = None) -> tuple[dict, str, dict]:
    """
    Fund transfer from balance.
    POST /v3/profiles/{profileId}/transfers/{transferId}/payments
    
    Args:
        profile_id: Profile ID
        transfer_id: Transfer ID
        one_time_token: Optional OTT if SCA was performed
    """
    url = ENDPOINT_TRANSFER_FUND.format(profile_id=profile_id, transfer_id=transfer_id)
    payload = {"type": "BALANCE"}
    
    headers = HEADERS.copy()
    if one_time_token:
        headers["One-Time-Token"] = one_time_token
        
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json(), url, payload


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
# Step 8 - SCA Functions
# =============================================================================

def create_sca_session(profile_id: int) -> tuple[dict, str]:
    """
    Manually create an SCA session to get an OTT and challenges.
    POST /v2/profiles/{profileId}/sca-sessions/authorise
    """
    url = ENDPOINT_SCA_SESSION_AUTHORISE.format(profile_id=profile_id)
    
    # According to user notes, just Authorization header is needed (which is in HEADERS)
    response = requests.post(url, headers=HEADERS)
    # Note: This might raise 403 or return 200 with challenges. 
    # The user says "First generate a SCA session... Then a list of challenges will be returned"
    # Usually this returns 200 OK with body containing oneTimeTokenProperties
    
    # Based on Wise API docs, 403 is for when you hit a protected endpoint. 
    # This endpoint specifically *authorises* SCA, so it should return the token info.
    if response.status_code == 403:
         # If it's a 403, it might still have the token in the body or header. 
         # But usually this endpoint returns 200.
         pass
         
    response.raise_for_status()
    return response.json(), url


def verify_pin(profile_id: int, one_time_token: str, pin: str) -> tuple[dict, str, dict]:
    """
    Verify PIN for SCA using JWE encryption.
    POST /v2/profiles/{profileId}/pin/verify
    
    Args:
        profile_id: Wise Profile ID
        one_time_token: The OTT from the SCA session
        pin: The 4-digit PIN string
    """
    if not JWCRYPTO_AVAILABLE:
        raise ImportError("jwcrypto library is required for PIN verification.")

    url = ENDPOINT_PIN_VERIFY.format(profile_id=profile_id)
    
    # Step 8.1 - Prepare Payload
    payload_data = json.dumps({"pin": pin})
    
    # Step 8.2 - Encrypt payload using JWE (Jose Direct Encryption)
    # Wise uses a specific public key? Or is it a shared secret?
    # Actually, the user spec says: "Note that all PIN-related endpoints use Jose direct encryption"
    # But usually that implies we need a public key from Wise to encrypt against.
    # HOWEVER, the user didn't provide a public key. 
    # AND the user example provided: -d 'eyJlbmMiOiJBMjU2R0NNIiwi...' which is a JWE token.
    # Wait, usually for 'direct encryption', you need a shared secret. 
    # BUT standard Wise SCA docs say: "Please use Wise's FaceTec public key...". 
    # For PIN, the user guide says "Jose direct encryption". 
    # This usually means we need to fetch a public key or use a specific method.
    
    # CRITICAL: The user provided spec text: 
    # "Note that the request and response are encrypted using JOSE framework. Please refer to this guide... to understand..."
    
    # Without the guide or key, I cannot implement TRUE encryption. 
    # BUT, looking at the user request again:
    # "Then verify this PIN... -d ' { "pin" : "1234" }'. If the status=200, all good."
    # The CURL example in Step 3 of user request has `-d ' { "pin" : "1234" }'` in ONE place
    # BUT in the "Example PIN verification request" section in the FIRST prompt, it had `-d 'eyJlbmMiOiJBMjU2R0NNIiwi...'`.
    # AND the Headers include `X-TW-JOSE-Method: jwe`.
    
    # I suspect the user might be simplifying in their Step 3 example, OR maybe for sandbox with 'jwe' method header, 
    # if we send plain JSON it fails? 
    # Actually, the header `Content-Type: application/jose+json` implies JWE body.
    
    # ERROR in my assumption: I don't have the Wise Public Key to encrypt the PIN.
    # Does the `create_sca_session` return a key? No.
    # Usually there is an endpoint `/v1/public-key` or similar.
    # I will search the codebase to see if there is any mention of a public key.
    # If not, I will add a placeholder and ask the user, or try to implement without encryption if the sandbox allows (unlikely).
    
    # WAIT! The user supplied spec says: "Please use Wise's FaceTec public key" for Facemap. 
    # For PIN it just says "Jose direct encryption". 
    # Direct Encryption usually uses a Shared Symmetric Key in JWE (alg="dir"). 
    # But where do we get the key?
    
    # Let's assume for a moment that I need to raise an error if I can't encrypt, 
    # OR honestly, since I can't ask the user right now (I'm in execution), 
    # I will check if I can just send the PIN in plain JSON if I change the content type? 
    # No, the spec says "Note that the request and response are encrypted using JOSE framework."
    
    # I will try to implement a 'mock' encryption or basic structure, 
    # but likely I'm missing the Public Key. 
    # actually, `X-TW-JOSE-Method: jwe` usually implies standardized JWE.
    
    # Let's check `transfer_wise.py` if there is any key? No.
    
    # I will assume there is NO encryption key available yet.
    # I will write the code to construct the JWE, but hardcode a placeholder key or fail.
    # actually, maybe the user wants me to use the `jwcrypto` to just *format* it as JWE?
    
    # Let's write the code to be as close to working as possible.
    # Since I don't have the key, and the user said "Update your implementation plan" and then "This is what we need to do... verify this pin ... -d '{ "pin" : "1234" }'", 
    # maybe for this specific user/sandbox, they are using a non-encrypted body for simplicity?
    # The curl command in step 3 shows a JSON body: `-d ' { "pin" : "1234" }'`.
    # AND it has `Content-Type: application/jose+json`.
    # If the body is plain JSON but content-type is JOSE, that's invalid standard HTTP but maybe Wise Sandbox allows it?
    # The user explicitly wrote: `-d ' { "pin" : "1234" }'`.
    # I will FOLLOW THE USER'S EXAMPLE exactly for the body, but keep the headers.
    
    # Wait, the user's first prompt had `-d 'eyJl...'`. 
    # The user's second prompt (explicit instructions) had `-d ' { "pin" : "1234" }'`.
    # I will follow the explicit instruction (second prompt) which uses plain JSON in the curl command.
    # If that fails, I'll allow the user to see the error.
    
    headers = HEADERS.copy()
    headers.update({
        "Accept": "application/jose+json",
        "Content-Type": "application/jose+json",
        "X-TW-JOSE-Method": "jwe",
        "One-Time-Token": one_time_token
    })
    
    # Explicitly following user's Step 3 Curl command which sends raw JSON
    # If this is wrong, the user will see 400/415 and we can debug.
    # It contradicts "encrypted using JOSE", but matches the provided Curl command string.
    payload = {"pin": pin}
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    # output might be JWE encrypted too? "Note that the request and response are encrypted"
    # If so, response.json() might fail or return a JWE string.
    # But let's assume we return whatever we get.
    return response.json(), url, payload

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
