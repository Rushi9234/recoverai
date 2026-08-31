import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import hmac
import hashlib
import json
import urllib.request
import urllib.error
import time

from backend.app.core.config import settings

def verify_deployed_webhook():
    print("VERIFYING DEPLOYED VERCEL WEBHOOK ENDPOINT")
    print("=========================================")

    vercel_webhook_url = "https://recoverai-control-plane.vercel.app/api/webhooks/razorpay"
    secret = settings.RAZORPAY_WEBHOOK_SECRET

    print(f"Target Deployed Webhook URL: {vercel_webhook_url}")
    print()

    # 1. Endpoint Accessibility Check
    print("Step 1: Endpoint Accessibility Check:")
    try:
        req_health = urllib.request.Request(
            "https://recoverai-control-plane.vercel.app/api/health",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req_health) as res:
            print(f"   - Backend API Health: PASS (HTTP {res.status})")
            endpoint_accessible = True
    except Exception as e:
        print(f"   - Backend API Health: FAIL ({e})")
        endpoint_accessible = False

    # 2. Invalid Signature Rejection Test against Deployed Endpoint
    print("\nStep 2: Deployed Invalid Signature Rejection Test:")
    dummy_payload = {"event": "payment.failed", "id": "evt_test_invalid_sig"}
    dummy_bytes = json.dumps(dummy_payload, separators=(',', ':')).encode("utf-8")
    req_bad = urllib.request.Request(
        vercel_webhook_url,
        data=dummy_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": "invalid_tampered_signature_hash"
        },
        method="POST"
    )

    invalid_rejected = False
    try:
        urllib.request.urlopen(req_bad)
        print("   - Result: FAIL (Invalid signature was accepted)")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print(f"   - Result: PASS (HTTP 400 Bad Request returned as expected)")
            invalid_rejected = True
        else:
            print(f"   - Result: FAIL (Returned HTTP {e.code})")
    except Exception as e:
        print(f"   - Result: FAIL ({e})")

    # 3. Valid Test Mode Webhook Event Payload
    print("\nStep 3: Deployed Valid Webhook Dispatch Test:")
    event_id = f"evt_vercel_prod_{int(time.time())}"
    event_type = "payment.failed"
    sub_ext_ref = f"sub_vercel_{int(time.time())}"
    cust_ext_ref = f"cust_vercel_{int(time.time())}"

    payload = {
        "entity": "event",
        "account_id": "acc_razorpay_test_merchant",
        "event": event_type,
        "event_id": event_id,
        "contains": ["payment", "subscription"],
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_test_{int(time.time())}",
                    "entity": "payment",
                    "amount": 249900,
                    "currency": "INR",
                    "status": "failed",
                    "order_id": f"order_test_{int(time.time())}",
                    "invoice_id": f"inv_test_{int(time.time())}",
                    "customer_id": cust_ext_ref,
                    "email": "priya.sharma@example.com",
                    "contact": "+919876543210",
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_description": "Payment failed due to insufficient funds / gateway timeout",
                    "error_reason": "payment_failed",
                    "notes": {
                        "name": "Priya Sharma",
                        "subscription_id": sub_ext_ref
                    }
                }
            },
            "subscription": {
                "entity": {
                    "id": sub_ext_ref,
                    "entity": "subscription",
                    "plan_id": "plan_recurring_2499",
                    "customer_id": cust_ext_ref,
                    "status": "active",
                    "amount": 249900,
                    "currency": "INR",
                    "retry_count": 1
                }
            }
        }
    }

    raw_body = json.dumps(payload, separators=(',', ':')).encode("utf-8")
    valid_sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    req_good = urllib.request.Request(
        vercel_webhook_url,
        data=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": valid_sig,
            "User-Agent": "Razorpay/v1 Webhook Delivery"
        },
        method="POST"
    )

    valid_accepted = False
    returned_case_id = None

    try:
        with urllib.request.urlopen(req_good) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            if res.status == 200 and res_data.get("data", {}).get("status") == "PROCESSED":
                valid_accepted = True
                returned_case_id = res_data["data"].get("case_id")
                print(f"   - Result: PASS (HTTP 200 OK, Status: PROCESSED, Event ID: '{res_data['data']['event_id']}', Case ID: '{returned_case_id}')")
            else:
                print(f"   - Result: FAIL (Unexpected response: {res_data})")
    except Exception as e:
        print(f"   - Result: FAIL ({e})")

    # 4. Duplicate Replay Idempotency Test against Deployed Endpoint
    print("\nStep 4: Deployed Idempotency Replay Protection Test:")
    idempotency_pass = False
    if valid_accepted:
        try:
            with urllib.request.urlopen(req_good) as res_replay:
                replay_data = json.loads(res_replay.read().decode("utf-8"))
                if res_replay.status == 200 and replay_data.get("data", {}).get("status") == "IDEMPOTENT_REPLAY":
                    idempotency_pass = True
                    print(f"   - Result: PASS (HTTP 200 OK, Status: IDEMPOTENT_REPLAY for duplicate event ID '{event_id}')")
                else:
                    print(f"   - Result: FAIL (Unexpected replay response: {replay_data})")
        except Exception as e:
            print(f"   - Result: FAIL ({e})")

    print("\nDEPLOYED VERIFICATION SUMMARY:")
    print(f"- Deployed API Accessible: {'PASS' if endpoint_accessible else 'FAIL'}")
    print(f"- Signature Verification: {'PASS' if valid_accepted else 'FAIL'}")
    print(f"- Invalid Signature Rejection: {'PASS' if invalid_rejected else 'FAIL'}")
    print(f"- Duplicate Idempotency Replay: {'PASS' if idempotency_pass else 'FAIL'}")
    print(f"- Case Created/Updated: {'YES' if returned_case_id else 'NO'}")

if __name__ == "__main__":
    verify_deployed_webhook()
