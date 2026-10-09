"""
Kafka producer for HR Employee Attrition data.
Reads the cleaned CSV and sends each employee as a JSON message to Kafka.
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import kafka  # kafka-python-ng package
from kafka import KafkaProducer

# Import config from the same directory
from config import BOOTSTRAP_SERVERS, TOPIC, CSV_PATH


def serialize_record(record: dict) -> dict:
    """
    Convert pandas types to plain Python types for JSON serialization.
    Ensures numeric columns are sent as JSON numbers, text as strings.
    Also adds an event timestamp.
    """
    # Convert to plain Python types
    serialized = {}
    for key, value in record.items():
        # Handle NaN/NA values
        if pd.isna(value):
            serialized[key] = None
        # Handle pandas Series/numpy types
        elif hasattr(value, 'dtype'):
            # Numeric types: convert to int or float (preserves JSON numbers)
            if pd.api.types.is_integer(value):
                serialized[key] = int(value)
            elif pd.api.types.is_float(value):
                serialized[key] = float(value)
            elif pd.api.types.is_bool(value):
                serialized[key] = bool(value)
            else:
                # Other types (strings, objects): convert to string
                serialized[key] = str(value)
        else:
            # Already a plain Python type (int, float, str, bool)
            serialized[key] = value
    
    # Add event timestamp in ISO 8601 format
    serialized['event_timestamp'] = datetime.now(timezone.utc).isoformat()
    # Provenance metadata to distinguish production records from test payloads
    serialized['record_type'] = 'production_employee'
    serialized['source_dataset'] = 'employees_clean.csv'
    
    return serialized


def send_employee_data(delay: float = 0.1, limit: int = None):
    """
    Read employee data from CSV and send to Kafka topic.
    
    Args:
        delay: Seconds to wait between messages (default 0.1)
        limit: Maximum number of records to send (None = all)
    """
    # Verify CSV exists
    csv_path = Path(CSV_PATH)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")
    
    # Read the cleaned CSV
    print(f"Reading data from: {CSV_PATH}")
    df = pd.read_csv(csv_path)
    total_records = len(df)
    
    if limit and limit < total_records:
        df = df.head(limit)
        print(f"Limiting to {limit} records out of {total_records}")
    else:
        print(f"Total records to send: {total_records}")
    
    # Create Kafka producer
    print(f"Connecting to Kafka at {BOOTSTRAP_SERVERS}")
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: str(k).encode('utf-8')
    )
    
    # Send each employee as a message
    sent_count = 0
    failure_count = 0
    
    for _, row in df.iterrows():
        employee_id = row['EmployeeNumber']
        
        # Prepare message
        record = row.to_dict()
        serialized = serialize_record(record)
        
        try:
            # Send message with EmployeeNumber as key
            future = producer.send(
                topic=TOPIC,
                key=employee_id,
                value=serialized
            )
            
            # Wait for send to complete (optional, for error detection)
            record_metadata = future.get(timeout=10)
            
            print(f"Sent Employee {employee_id} (partition {record_metadata.partition}, offset {record_metadata.offset})")
            sent_count += 1
            
            # Delay between messages to simulate streaming
            if delay > 0:
                time.sleep(delay)
                
        except Exception as e:
            print(f"Failed to send Employee {employee_id}: {e}")
            failure_count += 1
    
    # Flush and close producer
    producer.flush()
    producer.close()
    
    # Print summary
    print("\n" + "="*50)
    print("Producer Summary:")
    print(f"  Total attempted: {sent_count + failure_count}")
    print(f"  Successfully sent: {sent_count}")
    print(f"  Failures: {failure_count}")
    print("="*50)


def main():
    """Parse CLI arguments and run producer."""
    parser = argparse.ArgumentParser(
        description="Send HR employee data to Kafka topic"
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay in seconds between messages (default: 0.1)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of records to send (default: all)'
    )
    
    args = parser.parse_args()
    
    try:
        send_employee_data(delay=args.delay, limit=args.limit)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
