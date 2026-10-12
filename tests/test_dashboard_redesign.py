"""
Automated Unit and Integration Tests for Redesigned HR SaaS Dashboard.
Validates:
1. Authentication (PBKDF2 hashing, credential verification, rejection of invalid logins).
2. Data loading and ML prediction consistency.
3. Metric calculations matching UI reference (100 employees, 22 HR review, 36.4% avg risk).
4. Feature coefficient splitting and readable formatting.
"""

import os
import sys
from pathlib import Path

# Add project root and subdirectories to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "dashboard"))
sys.path.insert(0, str(PROJECT_ROOT / "hdfs"))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from dashboard.auth import hash_password, verify_password, authenticate, get_auth_config
from dashboard.data_loader import load_and_score_data, load_model_coefficients, format_feature_name


def test_authentication():
    print("Testing Authentication Module...")
    
    # 1. Test hash generation & verification
    test_pwd = "SecretPassword123!"
    pwd_hash, salt = hash_password(test_pwd)
    assert verify_password(test_pwd, salt, pwd_hash) is True, "Verification failed for correct password"
    assert verify_password("WrongPassword", salt, pwd_hash) is False, "Verification should fail for incorrect password"

    # 2. Test configured credentials
    cfg = get_auth_config()
    print(f"Configured Email: {cfg['email']}")
    assert "salt" in cfg and "hash" in cfg, "Config should contain salt and hash"

    # 3. Test authenticate function
    valid, msg = authenticate("hr@company.com", "hr123")
    assert valid is True, f"Valid login rejected: {msg}"

    # Also test username prefix
    valid_prefix, _ = authenticate("hr", "hr123")
    assert valid_prefix is True, "Username prefix login should succeed"

    # 4. Test invalid password
    invalid_pwd, msg = authenticate("hr@company.com", "wrongpass")
    assert invalid_pwd is False, "Invalid password should be rejected"

    # 5. Test empty inputs
    empty_res, msg = authenticate("", "")
    assert empty_res is False, "Empty inputs should be rejected"

    print(" Authentication tests passed successfully!\n")


def test_data_and_ml_metrics():
    print("Testing Data Loader & ML Inference...")
    
    # Load and score
    df, meta = load_and_score_data()
    assert not df.empty, "Dataframe should not be empty"
    
    total = meta["total_analyzed"]
    hr_review = meta["hr_review_count"]
    avg_risk = meta["avg_predicted_risk"]
    low = meta["low_count"]
    med = meta["med_count"]
    high = meta["high_count"]
    
    print(f"Total Analyzed: {total}")
    print(f"HR Review Required: {hr_review} ({meta['hr_review_pct']:.1f}%)")
    print(f"Avg Predicted Risk: {avg_risk:.1f}%")
    print(f"Risk Breakdown - Low: {low}, Med: {med}, High: {high}")
    
    # Verify values match reference image dataset
    assert total == 100, f"Expected 100 employees, got {total}"
    assert hr_review == 22, f"Expected 22 HR review records, got {hr_review}"
    assert round(avg_risk, 1) == 36.4, f"Expected 36.4% avg risk, got {round(avg_risk, 1)}%"
    assert low == 59, f"Expected 59 low risk, got {low}"
    assert med == 19, f"Expected 19 medium risk, got {med}"
    assert high == 22, f"Expected 22 high risk, got {high}"
    
    # Verify Top 5
    top_5 = meta["top_5"]
    assert len(top_5) == 5, f"Expected 5 records, got {len(top_5)}"
    top_ids = top_5["EmployeeNumber"].tolist()
    print(f"Top 5 Employee IDs: {top_ids}")
    assert top_ids[0] == 19, f"Expected top employee to be 19, got {top_ids[0]}"
    
    print(" Data loader & ML metric tests passed successfully!\n")


def test_feature_coefficients():
    print("Testing Feature Coefficients...")
    coeff_df = load_model_coefficients()
    assert not coeff_df.empty, "Feature coefficients should not be empty"
    
    pos = coeff_df[coeff_df["Coefficient"] > 0]
    neg = coeff_df[coeff_df["Coefficient"] < 0]
    
    print(f"Total Features: {len(coeff_df)}")
    print(f"Positive Coefficients (Risk Increasing): {len(pos)}")
    print(f"Negative Coefficients (Risk Reducing): {len(neg)}")
    
    assert len(pos) > 0, "Should have positive factors"
    assert len(neg) > 0, "Should have negative factors"
    
    top_pos_feature = pos.sort_values("Coefficient", ascending=False).iloc[0]["ReadableFeature"]
    top_neg_feature = neg.sort_values("Coefficient", ascending=True).iloc[0]["ReadableFeature"]
    print(f"Top positive driver: {top_pos_feature}")
    print(f"Top negative driver: {top_neg_feature}")
    
    assert "OverTime" in top_pos_feature, f"Expected OverTime to be top driver, got {top_pos_feature}"
    
    print(" Feature coefficients tests passed successfully!\n")


if __name__ == "__main__":
    print("=" * 70)
    print("STARTING TEST SUITE FOR REDESIGNED HR SAAS DASHBOARD")
    print("=" * 70)
    test_authentication()
    test_data_and_ml_metrics()
    test_feature_coefficients()
    print("=" * 70)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)
