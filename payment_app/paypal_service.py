import paypalrestsdk
from django.conf import settings
from django.utils import timezone
from urllib import request

import requests

paypalrestsdk.configure({
    "mode": "sandbox",  # change to live later
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET
})





def get_paypal_access_token():
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    client_id = settings.PAYPAL_CLIENT_ID
    secret = settings.PAYPAL_SECRET
    headers = {
    "Accept": "application/json",
    "Accept-Language": "en_US"
    }
    response = requests.post(
        url,
        auth=(client_id, secret),
        headers=headers,
        data={"grant_type": "client_credentials"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get access token: {response.text}")




def send_salary(payment):
    teacher = payment.payroll.teacher
    paypal_email = teacher.payment_account.paypalEmail
    try:
        if paypal_email:
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": f"batch_{payment.id}",
                    "email_subject": "Salary Payment"
                },
                "items": [
                    {
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": str(payment.amount),
                            "currency": "USD"
                        },
                        "receiver": paypal_email,
                        "note": "Monthly Salary",
                        "sender_item_id": str(payment.id)
                    }
                ]
            })
            try:
                if payout.create(sync_mode=False):
                    batch_id=payout.batch_header.payout_batch_id
                    payment.paypal_batch_id=batch_id
                    payment.status="PROCESSING"
                    payment.save()
                else:
                    payment.status="FAILED"
                    payment.save()
                    print(f"PayPal Error: {payout.error}")
                    raise Exception(f"PayPal Payout Error: {payout.error.get('message')}")
            except Exception as e:
                print(f"Detailed Error: {str(e)}")
                raise e
        else:
            print("Error: Teacher has no PayPal email configured.")
            payment.status = "FAILED"
            payment.save()

    except Exception as e:
        print(f"System Error: {str(e)}")
        raise e
    


def check_payout_status(batch_id, access_token):
    url = f"https://api.sandbox.paypal.com/v1/payments/payouts/{batch_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    print("STATUS API RESPONSE:", response.text)

    if response.status_code == 200:
        data = response.json()
        return data["batch_header"]["batch_status"]
    else:
        raise Exception(f"Error checking payouts status: {response.json()}")