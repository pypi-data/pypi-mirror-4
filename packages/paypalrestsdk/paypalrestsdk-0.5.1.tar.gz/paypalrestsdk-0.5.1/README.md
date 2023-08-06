# PayPal REST SDK [![Build Status](https://travis-ci.org/paypal/rest-api-sdk-python.png?branch=master)](https://travis-ci.org/paypal/rest-api-sdk-python)

The PayPal REST SDK provides Python APIs to create, process and manage payment.

## Installation

Install using `pip`:

```sh
pip install paypalrestsdk
```

From [Github](https://github.com/paypal/rest-api-sdk-python):

```sh
pip install git+https://github.com/paypal/rest-api-sdk-python.git
```

## Configuration

```python
import paypalrestsdk
paypalrestsdk.set_config(
  mode="sandbox", # sandbox or live
  client_id="EBWKjlELKMYqRNQ6sYvFo64FtaRLRR5BdHEESmha49TM",
  client_secret="EO422dn3gQLgDbuwqTjzrFgFtaRLRR5BdHEESmha49TM")
```

Configure through environment variables:

```sh
export PAYPAL_MODE=sandbox   # sandbox or live
export PAYPAL_CLIENT_ID=EBWKjlELKMYqRNQ6sYvFo64FtaRLRR5BdHEESmha49TM
export PAYPAL_CLIENT_SECRET=EO422dn3gQLgDbuwqTjzrFgFtaRLRR5BdHEESmha49TM
```

## Example

```python
import paypalrestsdk
import logging

logging.basicConfig(level=logging.INFO)

paypalrestsdk.set_config(
  mode="sandbox", # sandbox or live
  client_id="EBWKjlELKMYqRNQ6sYvFo64FtaRLRR5BdHEESmha49TM",
  client_secret="EO422dn3gQLgDbuwqTjzrFgFtaRLRR5BdHEESmha49TM")

payment = paypalrestsdk.Payment({
  "intent": "sale",
  "payer": {
    "payment_method": "credit_card",
    "funding_instruments": [{
      "credit_card": {
        "type": "visa",
        "number": "4417119669820331",
        "expire_month": "11",
        "expire_year": "2018",
        "cvv2": "874",
        "first_name": "Joe",
        "last_name": "Shopper" }}]},
  "transactions": [{
    "amount": {
      "total": "1.00",
      "currency": "USD" },
    "description": "This is the payment transaction description." }]})

if payment.create():
  print("Payment created successfully")
else:
  print(payment.error)
```

For more samples [github.com/paypal/rest-api-sdk-python/tree/master/samples](https://github.com/paypal/rest-api-sdk-python/tree/master/samples)

