import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import hmac
import hashlib
import json
import urllib.request
import urllib.error
from backend.app.core.config import settings

def run_webhook_verification():
    secret = settings.RAZORPAY_WEBHOOK_SECRET or "whsec_test_secret_12345"
    server_url = "http://localhost:8000/api/webhooks/razorpay"

    print("RAZORPAY WEBHOOK INTEGRATION VERIFICATION")
    print("-----------------------------------------")
    print(f"Target URL: {server_url}")
    print(f"Webhook Secret Configured: {'YES' if bool(settings.RAZORPAY_WEBHOOK_SECRET) else 'NO'}")
    print()

    # Test Payload
    event_id = "evt_test_razorpay_webhook_1001"
    payload = {
        "entity": "event",
        "account_id": "acc_test_merchant",
        "event": "subscription.charged",
        "event_id": event_id,
        "contains": ["subscription", "payment"],
        "payload": {
            "subscription": {
                "entity": {
                    "id": "sub_test_wh_101",
                    "customer_id": "cust_test_wh_202",
                    "plan_id": "plan_demo_101",
                    "status": "active",
                    "amount": 249900,
                    "currency": "INR",
                    "retry_count": 1
                }
            },
            "payment": {
                "entity": {
                    "id": "pay_test_wh_303",
                    "amount": 249900,
                    "currency": "INR",
                    "status": "captured",
                    "error_code": None
                }
            }
        }
    }
    raw_bytes = json.dumps(payload).encode("utf-8")
    valid_sig = hmac.new(secret.encode("utf-8"), raw_bytes, hashlib.sha256).hexdigest()

    # 1. Invalid Signature Test
    print("1. Invalid Signature Rejection Test:")
    req_bad = urllib.request.Request(
        server_url,
        data=raw_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": "invalid_signature_hash_xyz"
        },
        method="POST"
    )
    try:
        urllib.request.urlopen(req_bad)
        print("   - Result: FAIL (Invalid signature was accepted)")
        inv_sig_pass = False
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print(f"   - Result: PASS (HTTP 400 Bad Request correctly returned for invalid signature)")
            inv_sig_pass = True
        else:
            print(f"   - Result: FAIL (HTTP {e.code} returned instead of 400)")
            inv_sig_pass = False
    except Exception as e:
        print(f"   - Result: FAIL (Error: {e})")
        inv_sig_pass = False

    # 2. Valid Webhook Acceptance Test
    print("2. Valid Signature Acceptance Test:")
    req_good = urllib.request.Request(
        server_url,
        data=raw_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": valid_sig
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req_good) as res:
            res_body = json.loads(res.read().decode("utf-8"))
            if res.status == 200 and res_body.get("data", {}).get("status") == "PROCESSED":
                print(f"   - Result: PASS (HTTP 200 OK, Status: PROCESSED, Event ID: '{res_body['data']['event_id']}')")
                val_sig_pass = True
            else:
                print(f"   - Result: FAIL (Unexpected response: {res_body})")
                val_sig_pass = False
    except Exception as e:
        print(f"   - Result: FAIL (Error: {e})")
        val_sig_pass = False

    # 3. Duplicate Webhook Idempotency Test
    print("3. Duplicate Webhook Idempotency Replay Test:")
    try:
        with urllib.request.urlopen(req_good) as res:
            res_body = json.loads(res.read().decode("utf-8"))
            if res.status == 200 and res_body.get("data", {}).get("status") == "IDEMPOTENT_REPLAY":
                print(f"   - Result: PASS (HTTP 200 OK, Status: IDEMPOTENT_REPLAY for duplicate event ID '{event_id}')")
                idempotency_pass = True
            else:
                print(f"   - Result: FAIL (Unexpected response on replay: {res_body})")
                idempotency_pass = False
    except Exception as e:
        print(f"   - Result: FAIL (Error: {e})")
        idempotency_pass = False

    print()
    print("VERIFICATION SUMMARY:")
    print(f"- Invalid signature rejection: {'PASS' if inv_sig_pass else 'FAIL'}")
    print(f"- Valid signature acceptance: {'PASS' if val_sig_pass else 'FAIL'}")
    print(f"- Idempotency replay protection: {'PASS' if idempotency_pass else 'FAIL'}")

if __name__ == "__main__":
    run_webhook_verification()
