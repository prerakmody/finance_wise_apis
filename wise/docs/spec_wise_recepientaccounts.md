# Recipient Account

Recipient or beneficiary is the one who will receive the funds.

Recipient account endpoints use a mixture of our v1 and v2 APIs. Please ensure you address the right version to get the expected results.

All recipient IDs are cross compatible with v1 and v2.

Operations 

## The Recipient Account resource 

You're currently looking at v1. For new integrations please use the latest version.

Fields
id
accountId

profile
Personal or business profile ID. It is highly advised to pass the business profile ID in this field if your business account is managed by multiple users so that the recipient can be accessed by all users authorized on the business account.

user
User that created or owns this recipient

acccountHolderName
Recipient full name

currency
3 character country code

country
2 character currency code

type
Recipient type

ownedByCustomer
Whether this account is owned by the sending user.
Only include and set to true if the sender is also the recipient (eg when paying themselves).
Other personal details will be ignored.

details
Currency specific fields

details.legalType
Recipient legal type

details.sortCode
Recipient bank sort code (GBP example)

details.accountNumber
Recipient bank account no (GBP example)

Recipient Account Object

```json
{
    "id": 40000000,
    "business": null,
    "profile": 30000000,
    "accountHolderName": "John Doe",
    "currency": "GBP",
    "country": "GB",
    "type": "sort_code",
    "details": {
        "address": {
            "country": null,
            "countryCode": null,
            "firstLine": null,
            "postCode": null,
            "city": null,
            "state": null
        },
        "email": null,
        "legalType": "PRIVATE",
        "accountNumber": "37778842",
        "sortCode": "040075",
        "abartn": null,
        "accountType": null,
        "bankgiroNumber": null,
        "ifscCode": null,
        "bsbCode": null,
        "institutionNumber": null,
        "transitNumber": null,
        "phoneNumber": null,
        "bankCode": null,
        "russiaRegion": null,
        "routingNumber": null,
        "branchCode": null,
        "cpf": null,
        "cardNumber": null,
        "identificationNumber": null,
        "idType": null,
        "idNumber": null,
        "idCountryIso3": null,
        "idValidFrom": null,
        "idValidTo": null,
        "clabe": null,
        "swiftCode": null,
        "dateOfBirth": null,
        "clearingNumber": null,
        "bankName": null,
        "branchName": null,
        "businessNumber": null,
        "province": null,
        "city": null,
        "rut": null,
        "token": null,
        "cnpj": null,
        "payinReference": null,
        "pspReference": null,
        "orderId": null,
        "idDocumentType": null,
        "idDocumentNumber": null,
        "targetProfile": null,
        "taxId": null,
        "iban": null,
        "bic": null,
        "IBAN": null,
        "BIC": null,
        "interacAccount": null
    },
    "user": 10000000,
    "active": true,
    "ownedByCustomer": false
}
```

The v2 resource provides useful features such as the `accountSummary` and `longAccountSummary` field which can be used to represent the recipient's details in your UI. `displayFields` array allows you to build an UI containing all the dynamic fields of a recipient individually.

Additionally, the resource also includes a `hash` of a recipient, which can be used to track recipient details changes. This is a security feature to allow you to re-run any checks your system does on the recipient to validate them against, for example, fraud engines. The hash will remain constant unless the recipient's name or information in the `details` object changes.

Fields
id
ID of the recipient

creatorId
Account entity that owns the recipient account

profileId
Specific profile that owns the recipient account

name
Recipient name details

name.fullName
Recipient full name

name.givenName
Recipient first name

name.familyName
Recipient surname

name.middleName
Recipient middle name

currency
3 character currency code

country
2 character country code

type
Recipient type

legalEntityType
Entity type of recipient

status
Status of the recipient

details
Account details

details.reference
Recipient reference (GBP example)

details.sortCode
Recipient bank sort code (GBP example)

details.accountNumber
Recipient bank account no (GBP example)

details.hashedByLooseHashAlgorithm
Recipient account hash

commonFieldMap
Map of key lookup fields on the account

commonFieldMap.bankCodeField
Bank sort code identifier field

hash
Account hash for change tracking

accountSummary
Summary of account details for ease of lookup

accountSummary
Summary of account details for ease of lookup

longAccountSummary
Account details summary

displayFields
Lookup fields

displayFields.key
Account identifier key name

displayFields.label
Account identifier display label

displayFields.value
Account identifier value

ownedByCustomer
If recipient account belongs to profile owner

Recipient Account Object

```json
{
    "id": 40000000,
    "creatorId": 41000000,
    "profileId": 30000000,
    "name": {
        "fullName": "John Doe",
        "givenName": null,
        "familyName": null,
        "middleName": null,
        "patronymicName": null,
        "cannotHavePatronymicName": null
    },
    "currency": "GBP",
    "country": "GB",
    "type": "SortCode",
    "legalEntityType": "PERSON",
    "active": true,
    "details": {
        "reference": null,
        "accountNumber": "37778842",
        "sortCode": "040075",
        "hashedByLooseHashAlgorithm": "ad245621b974efa3ef870895c3wer419a3f01af18a8a5790b47645dba6304194"
    },
    "commonFieldMap": {
        "accountNumberField": "accountNumber",
        "bankCodeField": "sortCode"
    },
    "hash": "666ef880f8aa6113fa112ba6531d3ed2c26dd9fgbd7de5136bfb827a6e800479",
    "accountSummary": "(04-00-75) 37778842",
    "longAccountSummary": "GBP account ending in 8842",
    "displayFields": [
        {
            "key": "details/sortCode",
            "label": "UK sort code",
            "value": "04-00-75"
        },
        {
            "key": "details/accountNumber",
            "label": "Account number",
            "value": "37778842"
        }
    ],
    "isInternal": false,
    "ownedByCustomer": false
}
```

## Create a recipient account 

**`POST /v1/accounts`**

A **recipient** is a person or institution who is the ultimate beneficiary of your payment.

Recipient data includes three data blocks:

* General data - the personal details of an individual and basic information about a business.
* Bank details - account numbers, routing numbers, and other region-specific bank details.
* Address details - country and street address of an individual or business.


### General Data

* Recipient full name
* Legal type (private/business)
* Currency
* Date of Birth
* Owned by customer


Date of Birth is optional. Its usually not required, but consult with the /account-requirements APIs to confirm if it is needed, or contact Wise Support.

The `ownedbycustomer` is an optional boolean that indicates whether the recipient is the same entity (person or business) as the sender. Set it to `true` for self-transfers, such as a user sending money to their own account in another country or currency. We strongly recommend setting this field, as distinguishing self-transfers from third-party transfers improves routing and processing efficiency.

### Bank account data

There are many different variations of bank account details needed depending on recipient target currency. For example:

* GBP — sort code and account number
* BGN, CHF, DKK, EUR, GEL, GBP, NOK, PKR, PLN, RON, SEK — IBAN
* USD — routing number, account number, account type
* INR — IFSC code, account number
* etc.


### Address data

Recipient address data is required only if target currency is USD, PHP, THB or TRY, or if the source currency is USD or AUD.

* Country
* State (US, Canada, Brazil)
* City
* Address line
* Zip code


When creating recipient, the following general rules should be applied to the `accountHolderName` field:

* Full names for personal recipients.  They must include more than one name, and both first and last name must have more than one character. Numbers are not allowed in personal recipient names.
* Business names must be in full, but can be just a single name. The full name cannot be just a single character but can be made up of a set of single characters. e.g. "A" is not permitted but "A 1" or "A1" is permitted.
* Special characters `_()'*,.` are allowed for personal and business names.
* In general the following regex describes our permitted characters for a name: `[
    0-9A-Za-zÀ-ÖØ-öø-ÿ-_()'*,.\s
]`.


Recipient requirements will vary depending on recipient type.
A GBP example is provided here.
As you can see many of the fields are `null`, in order to know which fields are required for which currency we expose the [Recipients Requirements
](/api-reference/recipient#account-requirements) endpoint.

Request
currency
3 character currency code

type
Recipient type

profile
Personal or business profile ID. It is highly advised to pass the business profile ID in this field if your business account is managed by multiple users, so that the recipient can be accessed by all users authorized on the business account.

accountHolderName
Recipient full name

ownedByCustomer
Whether this account is owned by the sending user

details
Currency specific fields

details.legalType
Recipient legal type: PRIVATE or BUSINESS

details.sortCode
Recipient bank sort code (GBP example)

details.accountNumber
Recipient bank account no (GBP example)

details.dateOfBirth
Optional. Recipient Date of Birth in ISO 8601 date format.

#### Response

A complete [Recipient object
](/api-reference/recipient#object) is returned when created.

Example Request - GBP Recipient

```shell
curl -X \
  POST https: //api.wise-sandbox.com/v1/accounts \
  -H 'Authorization: Bearer <your api token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "currency": "GBP",
    "type": "sort_code",
    "profile": 30000000,
    "ownedByCustomer": true,
    "accountHolderName": "John Doe",
    "details": {
        "legalType": "PRIVATE",
        "sortCode": "040075",
        "accountNumber": "37778842",
        "dateOfBirth": "1961-01-01"
    }
}'
```

## Create a refund recipient account 

**`POST /v1/accounts?refund=true`**

Sometimes we may need to refund the transfer back to the sender  - see the [transfer status here
](/guides/product/send-money/tracking-transfers) for cases when this may happen.

A refund recipient is a person or institution where we will refund transfer the money back to if necessary. This is not always a mandatory resource to create. If the funds are sent over a fast local payment network we can usually infer the refund recipient from the bank transaction that funded the transfer. Please discuss this with your Wise implementation team if you are unsure if the refund recipient is needed.

If funds are sent using a slow domestic payment network, or you are using a bulk settlement model, we may require you to share the bank details of the source bank account.

#### Response

A complete [Recipient object
](/api-reference/recipient#object) is returned when created.

The refund recipient account ID returned here is used as `sourceAccount` when [creating transfers
](/guides/product/send-money/transfers#create).

The format of the request payload for refund recipient creation will be different depending on the currency you will send transfers from. This example is for GBP only. We can provide the correct format for your region upon request. You may use the Account-Requirements API to understand the payload requirements when creating the refund recipient for a specific currency.

Example Request - GBP Refund Recipient

```shell
curl -X POST \
  https: //api.wise-sandbox.com/v1/accounts?refund=true \
  -H 'Authorization: Bearer <your api token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "currency": "GBP",
    "type": "sort_code",
    "profile": 30000000,
    "details": {
        "accountHolderName": "John Doe",
        "legalType": "PRIVATE",
        "sortCode": "04-00-75",
        "accountNumber": "37778842"
    }
}'
```

## Create an email recipient account 

**`POST /v1/accounts`**

Please contact us before attempting to use email recipients. We do not recommend using this feature except for certain uses cases.

If you don't know recipient bank account details you can set up an email recipient; Wise will collect bank details directly from the recipient.

Wise will email your recipient with a link to collect their bank account details securely. After the bank account details have been provided Wise will complete your transfer.

Its best to confirm that this recipient type is available to your transaction by checking if the `"type": "email"` class is present in the response from `GET /v1/quotes/{
    {quoteId
    }
}/account-requirements` see [account requirements
](/api-reference/recipient#account-requirements) for more information on how to use this endpoint.

If planning to send multiple currencies to a single recipient, you will need to create a separate email recipient resource for this beneficiary, for every currency you intend to send to them.
We highly encourage you to provide the {profileId
} if your recipient is receiving a payment from your Business account, especially if you have multiple businesses, or have multiple users administrating your business account.

Please be aware of the following caveats:

* Testing of transfers to email recipients in sandbox is not currently possible.
* Recipients will be required to enter bank details **every time a payment is made.**
* We highly encourage you to provide the `profileId` if your recipient is receiving a payment from your Business account, especially if you have multiple businesses, or have multiple users administrating your business account.
* Please refer to our [help page
](https: //wise.com/help/articles/2932105/can-i-send-money-to-someone-with-only-their-email-address) on how this works and any additional constraints not mentioned in this section.


#### Response

A complete [Recipient object
](/api-reference/recipient#object) is returned when created.

Example Request - EUR Email Recipient

```shell
curl -X POST \
  https: //api.wise-sandbox.com/v1/accounts \
  -H 'Authorization: Bearer <your api token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "profile": 30000000,
    "accountHolderName": "John Doe",
    "currency": "EUR",
    "type": "email",
    "details": {
        "email": "john.doe@transfer-world.com"
    }
}'
```

## List recipient accounts 

**`GET /v1/accounts?profile={
    {profileId
    }
}&currency={
    {currency
    }
}`**

Fetch a list of the user's recipient accounts. Use the `currency` and `profile` parameters to filter by currency and/or the owning user profile ID. This list does not currently support pagination, therefore if please filter by currency to ensure a reasonable response time.

Both query parameters are optional.

Query Parameters
profileId
Filter by personal or business profile, returns only those owned by this profile.

currency
Filter responses by currency.

#### Response

An array of v1 [Recipient objects
](/api-reference/recipient#object) is returned.

Example Request

```shell
curl -X GET \
  https: //api.wise-sandbox.com/v1/accounts?profile={{profileId}}&currency={{currency}} \
  -H 'Authorization: Bearer <your api token>'
```

**`GET /v2/accounts?profileId={
    {profileId
    }
}&currency={
    {currency
    }
}`**

Fetch a list of the user's recipient accounts. Use the `profileId` parameter to filter by the profile who created the accounts, you should do this based on the personal or business profile ID you have linked to, based on your use case. Other filters are listed below for your convenience, for example `currency` is a useful filter to use when presenting the user a list of recipients to chose from in the case they have already submitted the target currency of their in your flow.

### Pagination

Pagination is supported for this endpoint. The response includes the `seekPositionForNext` and `size` parameters to manage this.

It works by setting `size` and `seekPosition` parameters in the call. Set the value in the `seekPositionForNext` of the previous response into the `seekPosition` parameter of your subsequent call in order to get the next page. To get the current page again, use the `seekPositionForCurrent` value.

### Sorting

You can also set the `sort` parameter to control the sorting of the response, for example:

`?sort=id,asc` sort by `id` ascending.
`?sort=id,desc` sort by id descending.
`?sort=currency,asc` sort by currency ascending.

All query parameters are optional.

Query Parameters
creatorId
Creator of the account.

profileId
Filter by personal or business profile, returns only those owned by this profile. Defaults to the personal profile.

currency
Filter responses by currency, comma separated values are supported (e.g. `USD,GBP`).

active
Filter by whether this profile is active. Defaults to `true`.

type
Filter responses by account type, comma separated values are supported (e.g. `iban,swift_code`).

ownedByCustomer
Filter to get accounts owned by the customer or not, leave out to get all accounts.

size
Page size of the response. Defaults to a maximum of 20.

seekPosition
Account ID to start the page of responses from in the response. `null` if no more pages.

sort
Sorting strategy for the response. Comma separated options: firstly either `id` or `currency`, followed by `asc` or `desc` for direction.

#### Response

An array of [Recipient objects
](/api-reference/recipient#object) is returned.

Example Request

```shell
curl -X GET \
  https: //api.wise-sandbox.com/v2/accounts?profile={{profileId}}&currency={{currency}} \
  -H 'Authorization: Bearer <your api token>'
```

Example Response

```json
{
    "content": [
        {
            "id": 40000000,
            "creatorId": 41000000,
            "profileId": 30000000,
            "name": {
                "fullName": "John Doe",
                "givenName": null,
                "familyName": null,
                "middleName": null,
                "patronymicName": null,
                "cannotHavePatronymicName": null
            },
            "currency": "GBP",
            "country": "GB",
            "type": "SortCode",
            "legalEntityType": "PERSON",
            "active": true,
            "details": {
                "reference": null,
                "accountNumber": "37778842",
                "sortCode": "040075",
                "hashedByLooseHashAlgorithm": "ad245621b974efa3ef870895c3wer419a3f01af18a8a5790b47645dba6304194"
            },
            "commonFieldMap": {
                "accountNumberField": "accountNumber",
                "bankCodeField": "sortCode"
            },
            "hash": "666ef880f8aa6113fa112ba6531d3ed2c26dd9fgbd7de5136bfb827a6e800479",
            "accountSummary": "(04-00-75) 37778842",
            "longAccountSummary": "GBP account ending in 8842",
            "displayFields": [
                {
                    "key": "details/sortCode",
                    "label": "UK sort code",
                    "value": "04-00-75"
                },
                {
                    "key": "details/accountNumber",
                    "label": "Account number",
                    "value": "37778842"
                }
            ],
            "isInternal": false,
            "ownedByCustomer": false
        }
    ],
    "sort": {
        "empty": true,
        "sorted": false,
        "unsorted": true
    },
    "size": 1
}
```

## Get account by ID 

**`GET /v1/accounts/{
    {accountId
    }
}`**

Get recipient account info by ID.

#### Response

A v1 [Recipient object
](/api-reference/recipient#object) is returned.

Example Request

```shell
curl -X GET \
  https: //api.wise-sandbox.com/v1/accounts/{{accountId}} \
  -H 'Authorization: Bearer <your api token>'
```

**`GET /v2/accounts/{
    {accountId
    }
}`**

V1 and v2 versions are cross compatible, but the v2 endpoint provides some additional features.
[Read more
](/api-reference/recipient#object).

Get recipient account info by ID.

#### Response

A [Recipient object
](/api-reference/recipient#object) is returned.

Example Request

```shell
curl -X GET \
  https: //api.wise-sandbox.com/v2/accounts/{{accountId}} \
  -H 'Authorization: Bearer <your api token>'
```

## Deactivate a recipient account 

**`DELETE /v2/accounts/{
    {accountId
    }
}`**

Deletes a recipient by changing its status to inactive (`"active": false`). Requesting to delete a recipient that is already inactive will return an HTTP status 403 (forbidden).

Only active recipients can be deleted and a recipient cannot be reactivated, however you can create a new recipient with the same details instead if necessary.

#### Response

A complete [Recipient object
](/api-reference/recipient#object) is returned, with the value of `active` set to `false`.

Example Request

```shell
curl -X DELETE \
  https: //api.wise-sandbox.com/v2/accounts/{{accountId}} \
  -H 'Authorization: Bearer <your api token>'
```

## Retrieve recipient account requirements dynamically 

All new integrations should use the v1.1 of `GET` and `POST` account requirements, enabled using the `Accept-Minor-Version` header.

#### Request

**` GET /v1/quotes/{
    {quoteId
    }
}/account-requirements`**
**` POST /v1/quotes/{
    {quoteId
    }
}/account-requirements`**
**` GET /v1/account-requirements?source=EUR&target=USD&sourceAmount=1000`**

You can use the data returned by this API to build a dynamic user interface for recipient creation. The `GET` and `POST` account-requirements endpoints help you to figure out which fields are required to create a valid recipient for different currencies. This is a step-by-step guide on how these endpoints work.

Use the `GET` endpoint to learn what datapoints are required to send a payment to your beneficiary. As you build that form, use the POST endpoint to learn if any additional datapoints are required as a result of passing a field that has `"refreshRequirementsOnChange": true'` in the `GET` response. You should be posting the same recipient account payload that will be posted to `v1/accounts`.

An example of this would be `address.country`. Some countries, like the United States, have a lower level organization, `"state" or "territory"`. After POSTing the recipient payload with address.country = "US", the list of possible states will appear in the response.

The third endpoint above is used to get account requirements for a specific currency route and amount without referring to a quote but with the amount, source and target currencies passed as URL parameters. Generally this approach is not recommended, you should have your user create a quote resource first and use this to generate the recipient account requirements. This is because some payout methods will only surface when the profile-context is known, for example (at the time of this writing), Business Payments to Chinese Yuan use a different payout method than what is revealed by `GET /v1/account-requirements?source=USD&target=CNY&sourceAmount=1000.`

These endpoints allow use of both v1 and v2 quotes using long or UUID based IDs, supporting legacy implementations using v1 quotes.

These endpoints accept an optional query parameter **originatorLegalEntityType**. When the transfer is initiated by a [Third Party Partner
](/guides/product/kyc/partner-accounts) we are not aware whether the actual sender is a business or person. In such cases, this parameter should be passed to receive correct requirements. The legal entity type should be one of the following values: `BUSINESS`, `PRIVATE`. This parameter is optional and the default value is the type of the partner profile.

Response
type
"address"

fields[n
].name
Field description

fields[n
].group[n
].key
Key is name of the field you should include in the JSON

fields[n
].group[n
].type
Display type of field. Can be `text`, `select`, `radio` or `date`

fields[n
].group[n
].refreshRequirementsOnChange
Tells you whether you should call POST account-requirements once the field value is set to discover required lower level fields.

fields[n
].group[n
].required
Indicates if the field is mandatory or not

fields[n
].group[n
].displayFormat
Display format pattern.

fields[n
].group[n
].example
Example value.

fields[n
].group[n
].minLength
Min valid length of field value.

fields[n
].group[n
].maxLength
Max valid length of field value.

fields[n
].group[n
].validationRegexp
Regexp validation pattern.

fields[n
].group[n
].validationAsync
Deprecated. This validation will instead be performed when submitting the request.

fields[n
].group[n
].valuesAllowed[n
].key
List of allowed values. Value key

fields[n
].group[n
].valuesAllowed[n
].name
List of allowed values. Value name.

Example Request

```shell
curl -X GET \
  https: //api.wise-sandbox.com/v1/quotes/{{quoteId}}/account-requirements \
  -H 'Authorization: Bearer <your api token>'
```

Please note that to use v1.1 `Accept-Minor-Version: 1` request header must be set.

### Request

**` GET /v1/quotes/{
    {quoteId
    }
}/account-requirements`**
**` POST /v1/quotes/{
    {quoteId
    }
}/account-requirements`**
**` GET /v1/account-requirements?source=EUR&target=USD&sourceAmount=1000`**

You can use the data returned by this API to build a dynamic user interface for recipient creation. The `GET` and `POST` account-requirements endpoints help you to figure out which fields are required to create a valid recipient for different currencies. This is a step-by-step guide on how these endpoints work.

Use the `GET` endpoint to learn what datapoints are required to send a payment to your beneficiary. As you build that form, use the POST endpoint to learn if any additional datapoints are required as a result of passing a field that has `"refreshRequirementsOnChange": true'` in the `GET` response. You should be posting the same recipient account payload that will be posted to `v1/accounts`.

An example of this would be `address.country`. Some countries, like the United States, have a lower level organization, `"state" or "territory"`. After POSTing the recipient payload with address.country = "US", the list of possible states will appear in the response.

The third endpoint above is used to get account requirements for a specific currency route and amount without referring to a quote but with the amount, source and target currencies passed as URL parameters. Generally this approach is not recommended, you should have your user create a quote resource first and use this to generate the recipient account requirements. This is because some payout methods will only surface when the profile-context is known, for example (at the time of this writing), Business Payments to Chinese Yuan use a different payout method than what is revealed by `GET /v1/account-requirements?source=USD&target=CNY&sourceAmount=1000.`

All new integrations should use the v1.1 of `GET` and `POST` account requirements, enabled using the `Accept-Minor-Version` header. It enables you to fetch the requirements including both the recipient name and email fields in the dynamic form, simplifying implementation of the form. Name and email address dynamic fields are required to support currencies such as KRW, JPY and RUB, and also remove the need for manual name validation.

These endpoints allow use of both v1 and v2 quotes using long or UUID based IDs, supporting legacy implementations using v1 quotes.

These endpoints accept an optional query parameter **originatorLegalEntityType**. When the transfer is initiated by a [Third Party Partner
](/guides/product/kyc/partner-accounts) we are not aware whether the actual sender is a business or person. In such cases, this parameter should be passed to receive correct requirements. The legal entity type should be one of the following values: `BUSINESS`, `PRIVATE`. This parameter is optional and the default value is the type of the partner profile.

Response
type
"address"

fields[n
].name
Field description

fields[n
].group[n
].key
Key is name of the field you should include in the JSON

fields[n
].group[n
].type
Display type of field. Can be `text`, `select`, `radio` or `date`

fields[n
].group[n
].refreshRequirementsOnChange
Tells you whether you should call POST account-requirements once the field value is set to discover required lower level fields.

fields[n
].group[n
].required
Indicates if the field is mandatory or not

fields[n
].group[n
].displayFormat
Display format pattern.

fields[n
].group[n
].example
Example value.

fields[n
].group[n
].minLength
Min valid length of field value.

fields[n
].group[n
].maxLength
Max valid length of field value.

fields[n
].group[n
].validationRegexp
Regexp validation pattern.

fields[n
].group[n
].validationAsync
Deprecated. This validation will instead be performed when submitting the request.

fields[n
].group[n
].valuesAllowed[n
].key
List of allowed values. Value key

fields[n
].group[n
].valuesAllowed[n
].name
List of allowed values. Value name.

Example Request

```shell
curl -X GET \
  https: //api.wise-sandbox.com/v1/quotes/{{quoteId}}/account-requirements \
  -H 'Authorization: Bearer <your api token>' \
  -H 'Accept-Minor-Version: 1'
```

Example Response from /account-requirements

```json
[
    {
        "type": "south_korean_paygate",
        "title": "PayGate",
        "usageInfo": null,
        "fields": [
            {
                "name": "E-mail",
                "group": [
                    {
                        "key": "email",
                        "name": "E-mail",
                        "type": "text",
                        "refreshRequirementsOnChange": false,
                        "required": true,
                        "displayFormat": null,
                        "example": "example@example.ex",
                        "minLength": null,
                        "maxLength": null,
                        "validationRegexp": "^[^\\s]+@[^\\s]+\\.[^\\s]{2,}$",
                        "validationAsync": null,
                        "valuesAllowed": null
                    }
                ]
            },
            {
                "name": "Recipient type",
                "group": [
                    {
                        "key": "legalType",
                        "name": "Recipient type",
                        "type": "select",
                        "refreshRequirementsOnChange": false,
                        "required": true,
                        "displayFormat": null,
                        "example": "",
                        "minLength": null,
                        "maxLength": null,
                        "validationRegexp": null,
                        "validationAsync": null,
                        "valuesAllowed": [
                            {
                                "key": "PRIVATE",
                                "name": "Person"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Full Name",
                "group": [
                    {
                        "key": "accountHolderName",
                        "name": "Full Name",
                        "type": "text",
                        "refreshRequirementsOnChange": false,
                        "required": true,
                        "displayFormat": null,
                        "example": "",
                        "minLength": 2,
                        "maxLength": 140,
                        "validationRegexp": "^[0-9A-Za-zÀ-ÖØ-öø-ÿ-_()'*,.%#^@{}~<>+$\"\\[\\]\\\\ ]+$",
                        "validationAsync": null,
                        "valuesAllowed": null
                    }
                ]
            },
            {
                "name": "Recipient's Date of Birth",
                "group": [
                    {
                        "key": "dateOfBirth",
                        "name": "Recipient's Date of Birth",
                        "type": "date",
                        "refreshRequirementsOnChange": false,
                        "required": true,
                        "displayFormat": null,
                        "example": "",
                        "minLength": null,
                        "maxLength": null,
                        "validationRegexp": "^\\d{4}\\-\\d{2}\\-\\d{2}$",
                        "validationAsync": null,
                        "valuesAllowed": null
                    }
                ]
            },
            {
                "name": "Recipient Bank Name",
                "group": [
                    {
                        "key": "bankCode",
                        "name": "Recipient Bank Name",
                        "type": "select",
                        "refreshRequirementsOnChange": false,
                        "required": true,
                        "displayFormat": null,
                        "example": "Choose recipient bank",
                        "minLength": null,
                        "maxLength": null,
                        "validationRegexp": null,
                        "validationAsync": null,
                        "valuesAllowed": [
                            {
                                "key": "",
                                "name": "Choose recipient bank"
                            },
              ...
                        ]
                    }
                ]
            },
            {
                "name": "Account number (KRW accounts only)",
                "group": [
                    {
                        "key": "accountNumber",
                        "name": "Account number (KRW accounts only)",
                        "type": "text",
                        "refreshRequirementsOnChange": false,
                        "required": true,
                        "displayFormat": null,
                        "example": "1254693521232",
                        "minLength": 10,
                        "maxLength": 16,
                        "validationRegexp": null,
                        "validationAsync": null,
                        "valuesAllowed": null
                    }
                ]
            }
        ]
    },
```

### Collecting Recipient Address

Normally our account requirements will instruct when a recipient address is required.
However, in some situations it's desirable to force the requirement so that an address can
be provided to Wise. To do this, add the query parameter `?addressRequired=true` to your request
and address will always be returned as a required field.

The JSON snippets are just example to illustrate demonstrating the recipient address fields. These fields are subject to change. Your integration should be built in a way to handle unrecognized or changed fields.

recipient.address requirements example

```json
...
  {
        "name": "Country",
        "group": [
            {
                "key": "address.country",
                "name": "Country",
                "type": "select",
                "refreshRequirementsOnChange": true,
                "required": true,
                "displayFormat": null,
                "example": "Choose a country",
                "minLength": null,
                "maxLength": null,
                "validationRegexp": null,
                "validationAsync": null,
                "valuesAllowed": [
          #list of countries
                ]
            }
        ]
    },
    {
        "name": "City",
        "group": [
            {
                "key": "address.city",
                "name": "City",
                "type": "text",
                "refreshRequirementsOnChange": false,
                "required": true,
                "displayFormat": null,
                "example": "",
                "minLength": 1,
                "maxLength": 255,
                "validationRegexp": "^.{1,255}$",
                "validationAsync": null,
                "valuesAllowed": null
            }
        ]
    },
    {
        "name": "Recipient address",
        "group": [
            {
                "key": "address.firstLine",
                "name": "Recipient address",
                "type": "text",
                "refreshRequirementsOnChange": false,
                "required": true,
                "displayFormat": null,
                "example": "",
                "minLength": 1,
                "maxLength": 255,
                "validationRegexp": "^.{1,255}$",
                "validationAsync": null,
                "valuesAllowed": null
            }
        ]
    },
    {
        "name": "Post code",
        "group": [
            {
                "key": "address.postCode",
                "name": "Post code",
                "type": "text",
                "refreshRequirementsOnChange": false,
                "required": true,
                "displayFormat": null,
                "example": "",
                "minLength": 1,
                "maxLength": 32,
                "validationRegexp": "^.{1,32}$",
                "validationAsync": null,
                "valuesAllowed": null
            }
        ]
    },
...
```