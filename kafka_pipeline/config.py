"""
Kafka configuration for the HR Employee Attrition pipeline.
All paths are absolute to work from any directory.
Environment variables can override defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists (optional - works without it)
load_dotenv()

# Build absolute project root from this config file's location
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Kafka connection settings
# Environment variables: BOOTSTRAP_SERVERS, TOPIC, GROUP_ID
BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "127.0.0.1:9092")
TOPIC = os.getenv("TOPIC", "employee-data")
GROUP_ID = os.getenv("GROUP_ID", "hr-consumer-group")

# Data file paths (absolute)
CSV_PATH = os.getenv(
    "CSV_PATH",
    str(PROJECT_ROOT / "data" / "processed" / "employees_clean.csv")
)

# Consumer settings
AUTO_OFFSET_RESET = os.getenv("AUTO_OFFSET_RESET", "earliest")
ENABLE_AUTO_COMMIT = os.getenv("ENABLE_AUTO_COMMIT", "true").lower() == "true"

# Batch size for consumer buffer
BATCH_SIZE = 100
