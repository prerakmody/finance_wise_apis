"""
Wise Transfer Streamlit App
Multi-step workflow for managing Wise transfers

### IMPORTANT: Dialog/Modal Handling Guidelines ###
# Streamlit only allows ONE dialog open at a time. To prevent the error:
# "StreamlitAPIException: Only one dialog is allowed to be opened at the same time"
#
# Follow these rules:
# 1. Each dialog must have its own session_state flag (e.g., show_profile_info_modal)
# 2. Before opening ANY dialog, CLOSE ALL OTHER dialogs by setting their flags to False
# 3. Only call the @st.dialog decorated function ONCE per script run
# 4. Use if st.session_state.show_xxx_modal: pattern AFTER all dialog function definitions
# 5. Never nest dialog calls or call multiple dialog functions in the same script run
#
# Pattern for opening a dialog:
#   if st.button("Open Dialog"):
#       st.session_state.show_other_modal_1 = False  # Close others first
#       st.session_state.show_other_modal_2 = False
#       st.session_state.show_this_modal = True
#
# Pattern for dialog definition:
#   @st.dialog("Title")
#   def show_dialog():
#       ... content ...
#       if st.button("Close"):
#           st.session_state.show_this_modal = False
#           st.rerun()
#
#   if st.session_state.show_this_modal:
#       show_dialog()
###
"""

import re
import json
import streamlit as st
import transfer_wise as wise
from config import BASE_CURRENCY_OPTIONS, ACCOUNT_CURRENCY_OPTIONS, COUNTRY_CODE_OPTIONS, SUPPORTED_CURRENCIES

# =============================================================================
# Step 1 - Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Wise Transfer Manager",
    page_icon="💸",
    layout="wide"
)

# =============================================================================
# Step 2 - Session State Initialization
# =============================================================================
if "profiles" not in st.session_state:
    st.session_state.profiles = []
if "selected_profile" not in st.session_state:
    st.session_state.selected_profile = None
if "recipients_by_currency" not in st.session_state:
    st.session_state.recipients_by_currency = {}
if "recipient_urls" not in st.session_state:
    st.session_state.recipient_urls = {}
if "profile_url" not in st.session_state:
    st.session_state.profile_url = None
if "selected_recipient" not in st.session_state:
    st.session_state.selected_recipient = None
if "current_quote" not in st.session_state:
    st.session_state.current_quote = None
if "current_quote_url" not in st.session_state:
    st.session_state.current_quote_url = None
if "current_transfer" not in st.session_state:
    st.session_state.current_transfer = None
if "pending_transfers" not in st.session_state:
    st.session_state.pending_transfers = []
if "base_currency" not in st.session_state:
    st.session_state.base_currency = "EUR"
if "previous_profile_id" not in st.session_state:
    st.session_state.previous_profile_id = None
if "show_new_recipient_modal" not in st.session_state:
    st.session_state.show_new_recipient_modal = False
if "show_profile_info_modal" not in st.session_state:
    st.session_state.show_profile_info_modal = False
if "show_recipient_info_modal" not in st.session_state:
    st.session_state.show_recipient_info_modal = False
if "show_quote_info_modal" not in st.session_state:
    st.session_state.show_quote_info_modal = False
if "show_transfer_input_modal" not in st.session_state:
    st.session_state.show_transfer_input_modal = False
if "show_transfer_output_modal" not in st.session_state:
    st.session_state.show_transfer_output_modal = False
if "show_fee_breakdown_modal" not in st.session_state:
    st.session_state.show_fee_breakdown_modal = False
if "transfer_api_input" not in st.session_state:
    st.session_state.transfer_api_input = None
if "transfer_api_output" not in st.session_state:
    st.session_state.transfer_api_output = None
if "profile_balances" not in st.session_state:
    st.session_state.profile_balances = []
if "quote_created" not in st.session_state:
    st.session_state.quote_created = False


# =============================================================================
# Step 2.1 - Helper function for resetting all modal states
# =============================================================================
def close_all_modals(except_modal: str = None):
    """
    Close all modal dialog states except the specified one.
    
    Args:
        except_modal: The modal key to keep open (optional)
    """
    modal_keys = [
        "show_new_recipient_modal",
        "show_profile_info_modal",
        "show_recipient_info_modal",
        "show_quote_info_modal",
        "show_transfer_input_modal",
        "show_transfer_output_modal",
        "show_fee_breakdown_modal",
    ]
    for key in modal_keys:
        if key != except_modal:
            st.session_state[key] = False


def open_modal(modal_key: str):
    """
    Open a modal by closing all others first and setting the target to True.
    
    Args:
        modal_key: The session state key for the modal to open
    """
    close_all_modals(except_modal=modal_key)
    st.session_state[modal_key] = True


def close_modal(modal_key: str):
    """
    Close a specific modal.
    Note: st.rerun() is NOT needed when closing dialogs - Streamlit handles this.
    
    Args:
        modal_key: The session state key for the modal to close
    """
    st.session_state[modal_key] = False


# =============================================================================
# Step 2.2 - Helper function for copy-to-clipboard with JSON content
# =============================================================================
def display_json_with_copy(data: dict, key_prefix: str, api_endpoint: str = None):
    """
    Display JSON data with a copy-to-clipboard button and optional API endpoint.
    
    Args:
        data: Dictionary to display and copy
        key_prefix: Unique key prefix for the copy button
        api_endpoint: Optional API endpoint string to display at top
    """
    # Step 2.2.0 - Display API endpoint if provided
    if api_endpoint:
        st.code(api_endpoint, language="bash")
    
    json_str = json.dumps(data, indent=2)
    
    # Step 2.2.1 - Display the copy button
    st.code(json_str, language="json", line_numbers=True)
    
    # Step 2.2.2 - Copy to clipboard button using data attribute
    st.text_input(
        "Copy the above JSON:",
        value=json_str,
        key=f"{key_prefix}_copy_input",
        label_visibility="collapsed",
        disabled=True
    )
    
    # Using st.components for clipboard functionality
    copy_button_html = f'''
    <button onclick="navigator.clipboard.writeText(document.getElementById('{key_prefix}_json').value).then(() => alert('Copied!'))" 
            style="padding: 5px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
        📋 Copy JSON
    </button>
    <input type="hidden" id="{key_prefix}_json" value='{json_str.replace("'", "&#39;").replace(chr(10), "&#10;")}'/>
    '''
    st.components.v1.html(copy_button_html, height=40)


# =============================================================================
# Step 2.3 - Generic Helper for Information Dialogs
# =============================================================================
def show_info_dialog(title: str, modal_key: str, data: dict, json_key_prefix: str, api_endpoint: str = None, subheader: str = None, empty_message: str = None):
    """
    Creates and displays a generic modal dialog for showing information/JSON.
    
    Args:
        title: The title of the dialog
        modal_key: The session state key to control visibility
        data: The dictionary data to display (if any)
        json_key_prefix: Prefix for JSON copy keys
        api_endpoint: Optional API endpoint string
        subheader: Optional subheader text
        empty_message: Message to show if data is missing
    """
    @st.dialog(title)
    def _dialog():
        if subheader:
            st.subheader(subheader)
        
        if data:
            formatted_endpoint = api_endpoint
            if api_endpoint and not api_endpoint.startswith("Used URL:") and "Used URL" not in api_endpoint:
                if "GET" in api_endpoint or "POST" in api_endpoint:
                     pass # keep as is
                else: 
                     formatted_endpoint = f"Used URL: {api_endpoint}"
            
            display_json_with_copy(data, json_key_prefix, api_endpoint=formatted_endpoint)
        elif empty_message:
            st.info(empty_message)
        
        if st.button("Close", use_container_width=True, key=f"close_{modal_key}"):
            close_modal(modal_key)
            st.rerun()

    if st.session_state.get(modal_key):
        _dialog()

# =============================================================================
# Step 2.4 - specific Dialog Function Definitions
# =============================================================================
@st.dialog("➕ Create New Recipient")
def show_create_recipient_dialog():
    if not st.session_state.selected_profile:
        st.error("No profile selected")
        return

    profile_id = st.session_state.selected_profile["id"]
    
    # Step 1: Select Target Currency
    target_currency = st.selectbox("Target Currency", SUPPORTED_CURRENCIES, key="modal_target_currency")
    
    # Step 2: Determine Source Currency (Dominant Balance)
    source_currency = "USD" # Default
    source_amount = 1.0 # Default to 1 unit as per requirements
    
    if st.session_state.profile_balances:
        try:
             # simple heuristic: just take the one with the highest number. 
            dominant_balance = max(st.session_state.profile_balances, key=lambda b: b.get("amount", {}).get("value", 0))
            source_currency = dominant_balance.get("amount", {}).get("currency", "USD")
        except Exception:
            pass
            
    # Display context
    st.caption(f"Fetching requirements for {source_currency} -> {target_currency} (Amount: {source_amount})")

    # Step 3: Fetch Requirements
    req_key = f"req_{source_currency}_{target_currency}"
    
    if req_key not in st.session_state:
        try:
            requirements, _ = wise.get_recipient_requirements(source_currency, target_currency, source_amount)
            st.session_state[req_key] = requirements
        except Exception as e:
            st.error(f"Error fetching requirements: {e}")
            st.session_state[req_key] = []

    requirements = st.session_state.get(req_key, [])
    
    # Step 4: Handle Multiple Recipient Types (Tabs)
    selected_requirement = None
    
    if not requirements:
        st.warning("No requirements found or error occurred.")
    else:
        # If multiple types (e.g., Local vs Swift vs Email), let user choose
        if len(requirements) > 1:
            req_options = {req.get("title", f"Option {i}"): i for i, req in enumerate(requirements)}
            selected_label = st.radio("Recipient Type", list(req_options.keys()), horizontal=True, key=f"req_type_select_{req_key}")
            selected_index = req_options[selected_label]
            selected_requirement = requirements[selected_index]
        else:
            selected_requirement = requirements[0]
            st.markdown(f"**{selected_requirement.get('title', 'Recipient Details')}**")

    # Step 5: Render Dynamic Form
    form_data = {}
    has_name_field = False
    
    if selected_requirement:
        # Determine the form 'type' (e.g. 'indian', 'aba')
        method_type = selected_requirement.get("type", "")
        
        fields_container = selected_requirement.get("fields", [])
        for field_container_idx, field_container in enumerate(fields_container):
            group = field_container.get("group", [])
            for field_idx, field_def in enumerate(group):
                key = field_def.get("key")
                label = field_def.get("name", key)
                field_type = field_def.get("type", "text")
                required = field_def.get("required", False)
                options = field_def.get("valuesAllowed", []) 
                
                # Check if this is the name field
                if key == "accountHolderName":
                    has_name_field = True
                
                # Make key unique per method type AND position to avoid collisions
                # We use field_container_idx and field_idx to be absolutely sure
                widget_key = f"field_{req_key}_{method_type}_{field_container_idx}_{field_idx}_{key}" 
                label_display = f"{label} {'*' if required else ''}"
                
                if field_type == "select" and options:
                    select_options = {}
                    for opt in options:
                        if isinstance(opt, dict):
                            select_options[opt.get("name")] = opt.get("key")
                        else:
                            select_options[str(opt)] = str(opt)
                    
                    selected_name = st.selectbox(label_display, list(select_options.keys()), key=widget_key)
                    form_data[key] = select_options.get(selected_name)
                    
                elif field_type == "radio" and options:
                     select_options = {}
                     for opt in options:
                        if isinstance(opt, dict):
                            select_options[opt.get("name")] = opt.get("key")
                        else:
                            select_options[str(opt)] = str(opt)
                     selected_name = st.radio(label_display, list(select_options.keys()), key=widget_key)
                     form_data[key] = select_options.get(selected_name)

                elif field_type == "text":
                     val = st.text_input(label_display, key=widget_key)
                     form_data[key] = val
                     
                     # Validation Logic
                     validation_regex = field_def.get("validationRegexp")
                     if validation_regex and val:
                         try:
                             if not re.match(validation_regex, val):
                                 st.caption(f":red[Invalid format. Expected pattern: `{validation_regex}`]")
                         except Exception:
                             pass # Regex might be complex or incompatible
                else:
                     val = st.text_input(label_display, key=widget_key)
                     form_data[key] = val

    # Step 6: Add Missing Fundamental Fields
    st.divider()
    st.subheader("General Recipient Info")
    
    # 6.1: Recipient Name (if not in dynamic fields)
    if not has_name_field:
        recipient_name = st.text_input("Recipient Full Name *", key="static_recipient_name")
        form_data["accountHolderName"] = recipient_name
    
    # 6.2: Owned by customer
    owned_by_customer = st.checkbox(
        "Is this account owned by you?", 
        value=False, 
        help="Check this if you are sending money to your own bank account.",
        key="static_owned_by_customer"
    )
    form_data["ownedByCustomer"] = owned_by_customer

    st.divider()
    
    col_create, col_cancel = st.columns(2)
    with col_create:
        if st.button("Create Recipient", type="primary", use_container_width=True):
            try:
                if not selected_requirement:
                    st.error("No requirement selected")
                else:
                    target_payload = {
                        "currency": target_currency,
                        "type": selected_requirement.get("type", ""), 
                        "profile": profile_id,
                        "ownedByCustomer": form_data.get("ownedByCustomer", False)
                    }

                    # Construct nested 'details' object
                    details = {}
                    top_level_keys = ["accountHolderName", "currency", "type", "profile", "ownedByCustomer"]
                    
                    for key, value in form_data.items():
                        if value is None or value == "": continue 
                        
                        # accountHolderName should be at root usually, but sometimes detailed.
                        # creating_recipient in transfer_wise.py helps handle this too.
                        if key in top_level_keys:
                            target_payload[key] = value
                        elif "." in key:
                             # Handle dot notation e.g. details.address.city
                             parts = key.split(".")
                             # Assuming standard wise structure where parts[0] is usually details
                             if parts[0] == "details":
                                 current_level = details
                                 for part in parts[1:-1]:
                                     if part not in current_level:
                                         current_level[part] = {}
                                     current_level = current_level[part]
                                 current_level[parts[-1]] = value
                             elif parts[0] == "address":
                                 # Put address inside details.address
                                 if "address" not in details: details["address"] = {}
                                 details["address"][parts[1]] = value
                        else:
                             details[key] = value
                    
                    if details:
                        target_payload["details"] = details
                    
                    # Debug Section (can be collapsed by default)
                    with st.expander("Debug Payload", expanded=False):
                        st.json(target_payload)

                    new_recipient, _ = wise.create_recipient(profile_id, target_payload)
                    
                    # Store result and show success
                    st.session_state.selected_recipient = new_recipient
                    st.success("✅ Recipient created successfully!")
                    
                    # Show the created JSON nicely
                    st.json(new_recipient)
                    
                    if st.button("Close & Use Recipient", type="primary", key="close_success_btn"):
                         st.session_state.show_new_recipient_modal = False
                         st.session_state.recipients_by_currency, st.session_state.recipient_urls = wise.get_all_recipients()
                         st.rerun()

            except Exception as e:
                st.error(f"Error creating recipient: {e}")
                if hasattr(e, 'response') and e.response is not None:
                     with st.expander("API Error Details"):
                         try:
                             st.json(e.response.json())
                         except:
                             st.text(e.response.text)

    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            close_modal("show_new_recipient_modal")
            st.rerun()

@st.dialog("💰 Fee Breakdown")
def show_fee_breakdown_dialog():
    quote = st.session_state.current_quote
    if not quote:
        st.error("No quote found")
        return

    payment_options = quote.get("paymentOptions", [])
    
    # Calculate display values again for the modal
    fee_display = "N/A"
    delivery_estimate = "N/A"
    for option in payment_options:
        if option.get("payIn") == "BALANCE":
            fee_obj = option.get("fee", {})
            fee_display = f"{fee_obj.get('total', 'N/A')} {fee_obj.get('currency', '')}"
            delivery_estimate = option.get("estimatedDelivery", "N/A")
            break
            
    st.code("POST /v3/profiles/{profileId}/quotes", language="bash")
    st.write(f"**Fee**: {fee_display}")
    st.write(f"**Delivery Estimate**: {delivery_estimate}")
    st.divider()
    st.divider()
    st.subheader("All Payment Options")
    # Sort options to put BALANCE first
    payment_options.sort(key=lambda x: 0 if x.get("payIn") == "BALANCE" else 1)
    
    for option in payment_options:
        pay_in = option.get("payIn", "Unknown")
        pay_out = option.get("payOut", "Unknown")
        fee_obj = option.get("fee", {})
        fee_total = fee_obj.get("total", "N/A")
        target_amt = option.get("targetAmount", "N/A")
        with st.expander(f"{pay_in} → {pay_out}"):
            st.write(f"**Target Amount**: {target_amt}")
            st.write(f"**Fee**: {fee_total}")
            st.write(f"**Estimated Delivery**: {option.get('estimatedDelivery', 'N/A')}")
    
    if st.button("Close", use_container_width=True, key="close_fee_modal"):
        close_modal("show_fee_breakdown_modal")
        st.rerun()


# =============================================================================
# Step 3 - Sidebar: Pending Transfers
# =============================================================================
with st.sidebar:
    st.header("📋 Pending Transfers")
    
    # Step 3.1 - Refresh button for pending transfers
    if st.button("🔄 Refresh Status", use_container_width=True):
        updated_transfers = []
        for t in st.session_state.pending_transfers:
            try:
                status, _ = wise.get_transfer_status(t["id"])
                t["status"] = status.get("status", "unknown")
            except Exception as e:
                t["status"] = f"Error: {e}"
            updated_transfers.append(t)
        st.session_state.pending_transfers = updated_transfers
        st.rerun()
    
    # Step 3.2 - Display pending transfers
    if st.session_state.pending_transfers:
        for transfer in st.session_state.pending_transfers:
            with st.container(border=True):
                st.markdown(f"**Transfer #{transfer['id']}**")
                st.write(f"Amount: {transfer.get('targetValue', 'N/A')} {transfer.get('targetCurrency', '')}")
                
                # Step 3.3 - Status badge with color
                status = transfer.get("status", "unknown")
                if status in ["completed", "outgoing_payment_sent"]:
                    st.success(f"✅ {status}")
                elif status in ["processing", "funds_converted"]:
                    st.info(f"⏳ {status}")
                elif status in ["cancelled", "bounced_back", "funds_refunded"]:
                    st.error(f"❌ {status}")
                else:
                    st.warning(f"⚠️ {status}")
    else:
        st.info("No pending transfers yet")
    
    st.divider()
    
    # Step 3.4 - Base currency selector
    st.subheader("⚙️ Settings")
    st.session_state.base_currency = st.selectbox(
        "Base Currency",
        options=BASE_CURRENCY_OPTIONS,
        index=BASE_CURRENCY_OPTIONS.index(st.session_state.base_currency)
    )


# =============================================================================
# Step 4 - Main Content
# =============================================================================
st.title("💸 Wise Transfer Manager")

# =============================================================================
# Step 5 - Step 0: Profile Selection
# =============================================================================
st.header("Step 0: Select Profile")

# Step 5.0 - Auto-load profiles on page load
if not st.session_state.profiles:
    try:
        st.session_state.profiles, st.session_state.profile_url = wise.get_profiles()
    except Exception as e:
        st.error(f"Error loading profiles: {e}")

if st.session_state.profiles:
    # Step 5.1 - Build profile display labels with rich details
    def get_profile_label(p):
        details = p.get("details", {})
        profile_type = p['type']
        if profile_type == "personal":
            first_name = details.get("firstName", "")
            last_name = details.get("lastName", "")
            name = f"{first_name} {last_name}".strip() or "Personal"
            avatar = details.get("avatar", "")
            avatar_info = f" 📷" if avatar else ""
            return f"👤 {name} (ID: {p['id']}){avatar_info}"
        else:
            business_name = details.get("name", "Business")
            website = details.get("website", "")
            website_info = f" 🌐 {website}" if website else ""
            return f"🏢 {business_name} (ID: {p['id']}){website_info}"
    
    profile_options = {
        get_profile_label(p): p 
        for p in st.session_state.profiles
    }
    
    # Step 5.2 - Layout: Dropdown | Info Button | Balances
    dropdown_col, info_col, balance_col = st.columns([2, 0.3, 2])
    
    with dropdown_col:
        selected_label = st.selectbox(
            "Choose Profile",
            options=list(profile_options.keys()),
            label_visibility="collapsed"
        )
        st.session_state.selected_profile = profile_options[selected_label]
        
        # Step 5.2.0 - Detect profile change and auto-load accounts
        current_profile_id = st.session_state.selected_profile["id"]
        if st.session_state.previous_profile_id != current_profile_id:
            st.session_state.previous_profile_id = current_profile_id
            # Step 5.2.0.1 - Reset all modal states on profile change
            close_all_modals()
            try:
                st.session_state.recipients_by_currency, st.session_state.recipient_urls = wise.get_all_recipients()
                # Step 5.2.0.2 - Fetch and store profile balances for source currency dropdown
                st.session_state.profile_balances, _ = wise.get_balances(current_profile_id)
            except Exception as e:
                st.error(f"Error auto-loading recipients: {e}")
    
    profile = st.session_state.selected_profile
    
    # Step 5.2.1 - Info button to show profile modal (exclusive - close other modals first)
    with info_col:
        if st.button("ℹ️", key="profile_info_btn", help="View profile details"):
            open_modal("show_profile_info_modal")
    
    # Step 5.2.2 - Profile info dialog modal (See dialog guidelines at top of file)
    # Step 5.2.2 - Profile info dialog modal is handled in Step 8 (Global Dialog Manager)
    pass
    
    # Step 5.3 - Display available balances on the right
    with balance_col:
        try:
            balances, _ = wise.get_balances(profile["id"])
            if balances:
                # Step 5.3.1 - Build balance string inline
                balance_parts = []
                for balance in balances:
                    amount_obj = balance.get("amount", {})
                    currency = amount_obj.get("currency", "")
                    value = amount_obj.get("value", 0)
                    if value != 0:  # Only show non-zero balances
                        balance_parts.append(f"**{currency}**: {value:,.2f}")
                if balance_parts:
                    st.markdown(" | ".join(balance_parts))
                else:
                    st.caption("No balances")
            else:
                st.caption("No balances")
        except Exception as e:
            st.caption(f"⚠️ {e}")
else:
    st.warning("Could not load profiles. Please check your API token.")

# =============================================================================
# Step 6 - Step 1: Recipient Selection / Creation
# =============================================================================
if st.session_state.selected_profile:
    st.divider()
    st.header("Step 1: Select or Create Recipient")
    
    profile_id = st.session_state.selected_profile["id"]
    
    col1, col2 = st.columns([3, 1])
    
    # Step 6.0.1 - Refresh and Add buttons side by side
    with col2:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🔄", help="Refresh recipients"):
                # Step 6.0.1.1 - Reset all modal states on refresh
                close_all_modals()
                try:
                    st.session_state.recipients_by_currency, st.session_state.recipient_urls = wise.get_all_recipients()
                    st.toast(f"Refreshed: {len(st.session_state.recipients_by_currency)} currencies")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        # Step 6.0.2 - Add button (exclusive - close other modals first)
        with btn_col2:
            if st.button("➕", help="Add new recipient"):
                open_modal("show_new_recipient_modal")
    
    # Step 6.1 - Display existing recipients grouped by currency
    with col1:
        if st.session_state.recipients_by_currency:
            # Step 6.2 - Build flat list of recipients with currency info
            all_recipients = []
            for currency, recipients in st.session_state.recipients_by_currency.items():
                for acc in recipients:
                    # Step 6.2.1 - Create new dict to avoid mutating original
                    acc_with_currency = dict(acc)
                    acc_with_currency["_currency"] = currency
                    all_recipients.append(acc_with_currency)
            
            if all_recipients:
                # Step 6.2.2 - Build display label using name.fullName or accountSummary
                def get_recipient_label(acc):
                    name_obj = acc.get("name", {})
                    full_name = name_obj.get("fullName", "") if isinstance(name_obj, dict) else ""
                    display_name = full_name or acc.get("accountHolderName", "Unknown")
                    summary = acc.get("accountSummary", "")
                    return f"{display_name} - {acc['_currency']} ({summary})"
                
                recipient_options = {
                    get_recipient_label(acc): acc
                    for acc in all_recipients
                }
                
                # Step 6.2.3 - Layout: Recipient dropdown | Info button
                acc_dropdown_col, acc_info_col = st.columns([0.9, 0.1])
                
                with acc_dropdown_col:
                    selected_acc_label = st.selectbox(
                        "Choose Existing Recipient",
                        options=list(recipient_options.keys()),
                        label_visibility="collapsed"
                    )
                    st.session_state.selected_recipient = recipient_options[selected_acc_label]
                
                # Step 6.3 - Info button to show recipient modal (exclusive - close other modals first)
                with acc_info_col:
                    if st.button("ℹ️", key="recipient_info_btn", help="View recipient details"):
                        open_modal("show_recipient_info_modal")
                
                # Step 6.3.1 - Recipient info dialog modal is handled in Step 8 (Global Dialog Manager)
                pass
            else:
                st.warning("No recipients found. Create one below.")
        else:
            st.info("Use 🔄 to refresh recipients or ➕ to add a new one")
    
    # Step 6.4 - Create new recipient modal dialog is customized in Step 2.4 and called in Step 8
    pass


# =============================================================================
# Step 7 - Step 2: Transfer Workflow
# =============================================================================
if st.session_state.selected_recipient and st.session_state.selected_profile:
    st.divider()
    st.header("Step 2: Create Transfer")
    
    profile_id = st.session_state.selected_profile["id"]
    recipient = st.session_state.selected_recipient
    target_currency = recipient.get("_currency") or recipient.get("currency", "EUR")
    
    # Step 7.0.1 - Build source currency options with balance info from profile balances
    currency_options = []  # Format: "EUR (1,234.56)"
    currency_map = {}  # Map display label back to currency code
    for balance in st.session_state.profile_balances:
        amount_obj = balance.get("amount", {})
        currency = amount_obj.get("currency", "")
        value = amount_obj.get("value", 0)
        if value > 0:  # Only include currencies with positive balance
            label = f"{currency} ({value:,.2f})"
            currency_options.append(label)
            currency_map[label] = currency
    
    # Step 7.0.2 - Fallback to base currency if no balances available
    if not currency_options:
        fallback_label = st.session_state.base_currency
        currency_options = [fallback_label]
        currency_map[fallback_label] = st.session_state.base_currency
    
    # Step 7.0.3 - Source currency, amount type, amount, and Create Quote button in single line
    quote_col1, quote_col2, quote_col3, quote_col4 = st.columns([1, 1, 1, 1])
    
    with quote_col1:
        selected_currency_label = st.selectbox(
            "Source Currency",
            options=currency_options,
            index=0,
            help="Select the currency to send from your balance",
            label_visibility="collapsed"
        )
        source_currency = currency_map[selected_currency_label]
    
    with quote_col2:
        amount_type = st.selectbox(
            "Amount Type",
            [f"Target Amount ({target_currency})", f"Source Amount ({source_currency})"],
            label_visibility="collapsed"
        )
    
    with quote_col3:
        amount = st.number_input("You send", min_value=0.01, value=100.0, step=10.0, label_visibility="collapsed", key="quote_amount_input")
    
    with quote_col4:
        # Step 7.0.3.1 - Create Quote button with refresh icon
        btn_col, refresh_col = st.columns([0.85, 0.15])
        with btn_col:
            create_quote_clicked = st.button("📝 Create Quote", use_container_width=True)
        with refresh_col:
            if st.button("🔄", key="quote_refresh_btn", help="Reset quote"):
                # Step 7.0.3.2 - Reset amount and clear quote
                st.session_state.current_quote = None
                st.session_state.current_quote_url = None
                close_all_modals()
                st.rerun()
    
    # Step 7.0.4 - Reset quote modal if source currency changed
    if "previous_source_currency" not in st.session_state:
        st.session_state.previous_source_currency = source_currency
    if st.session_state.previous_source_currency != source_currency:
        st.session_state.previous_source_currency = source_currency
        st.session_state.show_quote_info_modal = False
    
    # =========================================================================
    # Step 7.1 - Create Quote (button handler)
    # =========================================================================
    if create_quote_clicked:
        # Step 7.1.1 - Reset quote modal flag before creating new quote
        st.session_state.show_quote_info_modal = False
        try:
            if amount_type == f"Target Amount ({target_currency})":
                quote, quote_url = wise.create_quote(
                    profile_id=profile_id,
                    source_currency=source_currency,
                    target_currency=target_currency,
                    target_amount=amount
                )
            else:
                quote, quote_url = wise.create_quote(
                    profile_id=profile_id,
                    source_currency=source_currency,
                    target_currency=target_currency,
                    source_amount=amount
                )
            st.session_state.current_quote = quote
            st.session_state.current_quote_url = quote_url
            st.session_state.quote_created = True
            # Step 7.1.2 - Using compact checkbox mark instead of st.success bar to save screen real estate
        except Exception as e:
            st.session_state.quote_created = False
            st.error(f"Error creating quote: {e}")
    
    # =========================================================================
    # Step 7.2 - Confirm Quote
    # =========================================================================
    if st.session_state.current_quote:
        # Step 7.2 - Quote header with both info buttons on SAME LINE
        quote_header_col, quote_status_col, fee_info_col, quote_info_col = st.columns([0.7, 0.1, 0.1, 0.1])
        with quote_header_col:
            st.subheader("Step 2.2: Confirm Quote")
        with quote_status_col:
            # Step 7.2.0.1 - Compact checkbox indicator instead of full st.success bar
            if st.session_state.quote_created:
                st.markdown("✅", help="Quote created successfully")
        with fee_info_col:
            # Step 7.2.0.2 - Fee breakdown info button
            if st.button("ℹ️", key="fee_breakdown_btn", help="View fee breakdown"):
                open_modal("show_fee_breakdown_modal")
        with quote_info_col:
            # Step 7.2.0.3 - Quote details info button (on same line as fee breakdown)
            if st.button("📋", key="quote_info_btn", help="View quote details"):
                open_modal("show_quote_info_modal")
        
        quote = st.session_state.current_quote
        
        # Step 7.2.0.4 - Quote info dialog modal (See dialog guidelines at top of file)
        # Step 7.2.0.4 - Quote info dialog modal is handled in Step 8 (Global Dialog Manager)
        pass
        
        # Step 7.2.1 - Extract BOTH source and target amounts from paymentOptions for BALANCE payIn
        payment_options = quote.get("paymentOptions", [])
        source_amount_display = quote.get("sourceAmount", "N/A")  # Default from quote level
        target_amount_display = quote.get("targetAmount", "N/A")  # Default from quote level
        fee_display = "N/A"
        delivery_estimate = "N/A"
        for option in payment_options:
            if option.get("payIn") == "BALANCE":
                # Step 7.2.1.1 - Get source and target from the BALANCE payment option (more accurate)
                source_amount_display = option.get("sourceAmount", source_amount_display)
                target_amount_display = option.get("targetAmount", target_amount_display)
                fee_obj = option.get("fee", {})
                fee_display = f"{fee_obj.get('total', 'N/A')} {fee_obj.get('currency', '')}"
                delivery_estimate = option.get("estimatedDelivery", "N/A")
                break
        
        # Step 7.2.2 - Metrics display
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("You Send", f"{source_amount_display} {source_currency}", delta=f"- {fee_display}", delta_color="normal")
        with col2:
            st.metric("They Receive", f"{target_amount_display} {target_currency}")
        with col3:
            rate = quote.get("rate", "N/A")
            st.metric("Exchange Rate", f"1 {source_currency} = {rate} {target_currency}")
        
        # Step 7.2.3 - Fee breakdown dialog modal is customized in Step 2.4 and called in Step 8
        pass
        
        # =====================================================================
        # Step 7.3 - Create and Fund Transfer
        # =====================================================================
        st.subheader("Step 2.3: Send Transfer")
        
        reference = st.text_input("Transfer Reference (optional)", max_chars=35)
        
        # Step 7.3.0 - Transfer button with input/output info icons
        transfer_btn_col, input_info_col, output_info_col = st.columns([2, 0.3, 0.3])
        
        with transfer_btn_col:
            transfer_clicked = st.button("🚀 Create & Fund Transfer", type="primary", use_container_width=True)
        with input_info_col:
            # Step 7.3.0.0.1 - Close all other dialogs before opening (See dialog guidelines at top of file)
            if st.button("ℹ️", key="transfer_input_btn", help="View API input JSON"):
                open_modal("show_transfer_input_modal")
        with output_info_col:
            # Step 7.3.0.0.2 - Close all other dialogs before opening (See dialog guidelines at top of file)
            if st.button("📤", key="transfer_output_btn", help="View API output JSON"):
                open_modal("show_transfer_output_modal")
        
        # Step 7.3.0.1 - Transfer API input dialog (See dialog guidelines at top of file)
        # Step 7.3.0.1 - Transfer API input/output items are handled in Step 8 (Global Dialog Manager)
        pass
        
        if transfer_clicked:
            try:
                # Step 7.3.1 - Update quote with recipient
                quote_id = quote.get("id")
                recipient_id = recipient.get("id")
                
                updated_quote, update_url = wise.update_quote_with_recipient(
                    profile_id=profile_id,
                    quote_id=quote_id,
                    recipient_id=recipient_id
                )
                
                # Step 7.3.2 - Build transfer input payload for debugging
                import uuid
                transfer_input_payload = {
                    "targetAccount": recipient_id,
                    "quoteUuid": quote_id,
                    "customerTransactionId": "(generated UUID)",
                    "details": {"reference": reference}
                }
                st.session_state.transfer_api_input = {
                    "update_quote": {
                        "profile_id": profile_id,
                        "quote_id": quote_id,
                        "recipient_id": recipient_id
                    },
                    "create_transfer": transfer_input_payload,
                    "fund_transfer": {
                        "profile_id": profile_id,
                        "transfer_id": "(from create_transfer response)",
                        "payload": {"type": "BALANCE"}
                    }
                }
                
                # Step 7.3.3 - Create transfer
                transfer, transfer_url = wise.create_transfer(
                    quote_id=quote_id,
                    recipient_id=recipient_id,
                    reference=reference
                )
                
                transfer_id = transfer.get("id")
                
                # Step 7.3.4 - Fund transfer from balance
                funding, fund_url = wise.fund_transfer(profile_id, transfer_id)
                
                # Step 7.3.5 - Store output for debugging
                st.session_state.transfer_api_output = {
                    "create_transfer": {
                        "response": transfer,
                        "url": transfer_url
                    },
                    "fund_transfer": {
                        "response": funding,
                        "url": fund_url
                    }
                }
                
                # Step 7.3.6 - Save to pending transfers
                transfer["targetValue"] = quote.get("targetAmount")
                transfer["targetCurrency"] = target_currency
                transfer["status"] = transfer.get("status", "pending")
                st.session_state.pending_transfers.append(transfer)
                st.session_state.current_transfer = transfer
                
                st.success(f"✅ Transfer created and funded! ID: {transfer_id}")
                
                # Step 7.3.7 - Clear quote for next transfer
                st.session_state.current_quote = None
                
            except Exception as e:
                # Step 7.3.8 - Store error in output for debugging
                st.session_state.transfer_api_output = {
                    "error": str(e),
                    "input_used": st.session_state.transfer_api_input
                }
                st.error(f"Error creating/funding transfer: {e}")
        
        # =====================================================================
        # Step 7.4 - Track Transfer Status
        # =====================================================================
        if st.session_state.current_transfer:
            st.subheader("Step 2.4: Track Transfer")
            
            transfer = st.session_state.current_transfer
            transfer_id = transfer.get("id")
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if st.button("🔄 Refresh Status"):
                    try:
                        status, _ = wise.get_transfer_status(transfer_id)
                        st.session_state.current_transfer = status
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col1:
                status = transfer.get("status", "unknown")
                st.write(f"**Transfer ID**: {transfer_id}")
                st.write(f"**Status**: {status}")
                
                with st.expander("📄 Full Transfer Details"):
                    st.json(transfer)


# =============================================================================
# Step 8 - Global Dialog Manager (Render AFTER all logic)
# =============================================================================
# This section ensures that we checks the status of all modals AT THE END of the script
# This prevents race conditions where a dialog is rendered before a button click
# closes it, causing "multiple dialogs" errors.

if st.session_state.show_new_recipient_modal:
    show_create_recipient_dialog()

elif st.session_state.show_fee_breakdown_modal:
    show_fee_breakdown_dialog()

elif st.session_state.show_profile_info_modal and st.session_state.selected_profile:
    profile = st.session_state.selected_profile
    api_url = st.session_state.profile_url or "GET /v1/profiles"
    show_info_dialog(
        title="Profile Details",
        modal_key="show_profile_info_modal",
        data=profile,
        json_key_prefix="profile_info",
        api_endpoint=f"Used URL: {api_url}",
        subheader=f"Profile ID: {profile['id']}"
    )

elif st.session_state.show_recipient_info_modal and st.session_state.selected_recipient:
    acc = st.session_state.selected_recipient
    name_obj = acc.get("name", {})
    display_name = name_obj.get("fullName", "") if isinstance(name_obj, dict) else acc.get("accountHolderName", "Unknown")
    acc_currency = acc.get("_currency")
    api_url = st.session_state.recipient_urls.get(acc_currency, "GET /v2/accounts")
    show_info_dialog(
        title="Recipient Details",
        modal_key="show_recipient_info_modal",
        data=acc,
        json_key_prefix="recipient_info",
        api_endpoint=f"Used URL: {api_url}",
        subheader=f"{display_name}"
    )

elif st.session_state.show_quote_info_modal and st.session_state.current_quote:
    quote = st.session_state.current_quote
    api_url = st.session_state.current_quote_url or "POST /v3/profiles/{profileId}/quotes"
    show_info_dialog(
        title="Quote Details",
        modal_key="show_quote_info_modal",
        data=quote,
        json_key_prefix="quote_info",
        api_endpoint=f"Used URL: {api_url}",
        subheader=f"Quote ID: {quote.get('id', 'N/A')}"
    )

elif st.session_state.show_transfer_input_modal:
    show_info_dialog(
        title="📥 Transfer API Input JSON",
        modal_key="show_transfer_input_modal",
        data=st.session_state.transfer_api_input,
        json_key_prefix="transfer_input",
        api_endpoint="PATCH ... + POST ... + POST ...",
        empty_message="No transfer input available."
    )

elif st.session_state.show_transfer_output_modal:
    show_info_dialog(
        title="📤 Transfer API Output JSON",
        modal_key="show_transfer_output_modal",
        data=st.session_state.transfer_api_output,
        json_key_prefix="transfer_output",
        api_endpoint="POST ... + POST ...",
        empty_message="No transfer output available."
    )

# =============================================================================
# Step 9 - Footer
# =============================================================================
st.divider()
st.caption("💸 Wise Transfer Manager - Built with Streamlit")
