import joblib
import pandas as pd


MODEL_PATH = "ml/models/attrition_model.pkl"

RISK_THRESHOLD = 0.60


def load_model():
    """Load the trained attrition prediction model."""
    return joblib.load(MODEL_PATH)


def get_risk_level(probability):
    """Convert attrition probability into a risk category."""

    if probability >= 0.60:
        return "HIGH"
    elif probability >= 0.40:
        return "MEDIUM"
    else:
        return "LOW"


def predict_employee(model, employee_data):
    """
    Predict attrition risk for one or more employees.

    Parameters
    ----------
    model : trained sklearn pipeline
        The trained attrition model.

    employee_data : pandas.DataFrame
        Employee feature data.
        Must contain the same input features used during training.

    Returns
    -------
    pandas.DataFrame
        Employee data with probability, risk level and HR review flag.
    """

    # Make a copy so the original data is not modified
    data = employee_data.copy()

    # EmployeeNumber is an identifier and was not used for training
    if "EmployeeNumber" in data.columns:
        employee_ids = data["EmployeeNumber"]
        data = data.drop(columns=["EmployeeNumber"])
    else:
        employee_ids = None

    # Remove target column if it happens to be present
    if "Attrition" in data.columns:
        data = data.drop(columns=["Attrition"])

    # Predict probability of Attrition = Yes
    probabilities = model.predict_proba(data)[:, 1]

    results = pd.DataFrame({
        "AttritionProbability": probabilities.round(4)
    })

    results["RiskLevel"] = results[
        "AttritionProbability"
    ].apply(get_risk_level)

    results["HRReview"] = results[
        "AttritionProbability"
    ].apply(
        lambda probability:
        "YES" if probability >= RISK_THRESHOLD else "NO"
    )

    if employee_ids is not None:
        results.insert(
            0,
            "EmployeeNumber",
            employee_ids.values
        )

    return results


def predict_from_csv(input_path):
    """Predict attrition risk for employees in a CSV file."""

    model = load_model()

    employee_data = pd.read_csv(input_path)

    return predict_employee(
        model,
        employee_data
    )


if __name__ == "__main__":

    print("=" * 70)
    print("EMPLOYEE ATTRITION RISK PREDICTION")
    print("=" * 70)

    input_path = "data/processed/employees_clean.csv"

    model = load_model()

    print("\nModel loaded successfully.")

    employee_data = pd.read_csv(input_path)

    results = predict_employee(
        model,
        employee_data
    )

    print("\n" + "=" * 70)
    print("RISK SUMMARY")
    print("=" * 70)

    print(results["RiskLevel"].value_counts())

    print("\nHR Review Required:")
    print(results["HRReview"].value_counts())

    print("\n" + "=" * 70)
    print("HIGH-RISK EMPLOYEES")
    print("=" * 70)

    high_risk = (
        results[
            results["RiskLevel"] == "HIGH"
        ]
        .sort_values(
            "AttritionProbability",
            ascending=False
        )
    )

    print(
        high_risk.head(20).to_string(
            index=False
        )
    )

    output_path = (
        "ml/results/"
        "employee_risk_predictions.csv"
    )

    results.to_csv(
        output_path,
        index=False
    )

    print("\nPredictions saved to:")
    print(output_path)

    print("\n" + "=" * 70)
    print("RISK PREDICTION COMPLETED")
    print("=" * 70)