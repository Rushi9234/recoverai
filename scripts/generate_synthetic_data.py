import json
import random
import os

def generate_datasets():
    categories_distribution = [
        ("INSUFFICIENT_FUNDS", "low_balance", "RETRY_LATER", 0.20),
        ("EXPIRED_PAYMENT_METHOD", "card_expired", "PAYMENT_METHOD_RECOVERY", 0.15),
        ("REPEATED_DECLINE", "do_not_honor", "HUMAN_ESCALATION", 0.15),
        ("TRANSIENT_TECHNICAL_FAILURE", "gateway_timeout", "RETRY_LATER", 0.15),
        ("RETRY_BUDGET_EXHAUSTED", "max_retries_exceeded", "HUMAN_ESCALATION", 0.10),
        ("SUCCESSFUL_RETRY", "gateway_timeout", "RETRY_LATER", 0.10),
        ("DUPLICATE_EVENT", "duplicate_webhook", "STOP", 0.05),
        ("MANDATE_OR_CUSTOMER_ACTION_REQUIRED", "mandate_inactive", "PAYMENT_METHOD_RECOVERY", 0.05),
        ("UNKNOWN_OR_UNRESOLVED", "unknown_code_99", "HUMAN_ESCALATION", 0.05),
    ]

    def build_case(idx, cat, code, action):
        case_id = f"synth_case_{idx:04d}"
        sub_id = f"sub_synth_{idx:04d}"
        cust_id = f"cust_synth_{idx:04d}"
        inv_id = f"inv_synth_{idx:04d}"
        amount = random.choice([49900, 99900, 149900, 249900, 499900, 999900, 1499900])
        attempt_count = 3 if cat == "RETRY_BUDGET_EXHAUSTED" else random.choice([1, 2])
        
        case_item = {
            "case_id": case_id,
            "external_event_id": f"evt_synth_{idx:04d}",
            "customer_id": cust_id,
            "subscription_id": sub_id,
            "invoice_id": inv_id,
            "amount_minor": amount,
            "currency": "INR",
            "failure_code": code,
            "attempt_count": attempt_count,
            "max_attempts": 3,
            "successful_payments": random.randint(0, 12),
            "days_since_failure": random.choice([0, 1, 2, 5]),
            "expected_category": cat,
            "expected_action": action
        }
        
        ground_truth_item = {
            "case_id": case_id,
            "ground_truth_category": cat,
            "ground_truth_action": action,
            "ground_truth_should_contact": action in ["CUSTOMER_OUTREACH", "PAYMENT_METHOD_RECOVERY"],
            "ground_truth_recoverable": cat in ["TRANSIENT_TECHNICAL_FAILURE", "INSUFFICIENT_FUNDS", "EXPIRED_PAYMENT_METHOD", "SUCCESSFUL_RETRY"]
        }
        
        return case_item, ground_truth_item

    os.makedirs("data", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # 1. Generate 50 cases
    cases_50 = []
    ground_truth_map = {}
    
    count_50 = 50
    for idx in range(1, count_50 + 1):
        # Choose distribution
        r = random.random()
        cumulative = 0.0
        selected = categories_distribution[0]
        for item in categories_distribution:
            cumulative += item[3]
            if r <= cumulative:
                selected = item
                break
        cat, code, action, _ = selected
        c_item, g_item = build_case(idx, cat, code, action)
        cases_50.append(c_item)
        ground_truth_map[c_item["case_id"]] = g_item

    with open("data/synthetic_50.json", "w", encoding="utf-8") as f:
        json.dump(cases_50, f, indent=2)

    # 2. Generate 250 cases
    cases_250 = []
    for idx in range(1, 251):
        r = random.random()
        cumulative = 0.0
        selected = categories_distribution[0]
        for item in categories_distribution:
            cumulative += item[3]
            if r <= cumulative:
                selected = item
                break
        cat, code, action, _ = selected
        c_item, g_item = build_case(idx, cat, code, action)
        cases_250.append(c_item)
        if c_item["case_id"] not in ground_truth_map:
            ground_truth_map[c_item["case_id"]] = g_item

    with open("data/synthetic_250.json", "w", encoding="utf-8") as f:
        json.dump(cases_250, f, indent=2)

    # 3. Ground Truth
    with open("data/ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(ground_truth_map, f, indent=2)

    print("Successfully generated data/synthetic_50.json, data/synthetic_250.json, and data/ground_truth.json")

if __name__ == "__main__":
    generate_datasets()
