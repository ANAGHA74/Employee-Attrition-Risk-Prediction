"""
Verification script to check that all employee records were successfully
sent to the Kafka topic.
Creates a fresh consumer group to read from the beginning and counts messages.
"""

import sys
import time
from pathlib import Path

import pandas as pd
import kafka  # kafka-python-ng package
from kafka import KafkaConsumer

# Add kafka_pipeline to path for import
sys.path.insert(0, str(Path(__file__).resolve().parent / "kafka_pipeline"))
from config import BOOTSTRAP_SERVERS, TOPIC


def get_expected_count():
    """Read the CSV file and return the number of rows."""
    csv_path = Path(__file__).resolve().parent / "data" / "processed" / "employees_clean.csv"
    df = pd.read_csv(csv_path)
    return len(df)


def verify_message_count(timeout_seconds: int = 30):
    """
    Verify that the expected number of messages exist in the Kafka topic.
    Uses polling to avoid hanging, and reads the actual CSV row count.
    
    Args:
        timeout_seconds: Timeout for reading messages (default 30)
    """
    expected_count = get_expected_count()
    
    print(f"Verifying message count in topic '{TOPIC}'")
    print(f"Expected count (from CSV): {expected_count}")
    print(f"Using bootstrap servers: {BOOTSTRAP_SERVERS}")
    
    # Create a fresh consumer group for verification (unique per run)
    verification_group_id = f"verify-{int(time.time())}"
    
    try:
        # Create consumer to read from beginning
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            group_id=verification_group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda m: m.decode('utf-8')  # Just count, don't deserialize
        )
        
        # Get partition info
        partitions = consumer.partitions_for_topic(TOPIC)
        if not partitions:
            print(f"ERROR: Topic '{TOPIC}' not found or has no partitions")
            return False
        
        print(f"Topic has {len(partitions)} partition(s)")
        
        # Count messages using polling (avoids hanging)
        message_count = 0
        start_time = time.time()
        
        print("Counting messages...")
        while True:
            # Poll with 1 second timeout to check for completion
            raw_records = consumer.poll(timeout_ms=1000)
            
            # Process polled messages
            for topic_partition, messages in raw_records.items():
                message_count += len(messages)
            
            # Print progress every 100 messages
            if message_count > 0 and message_count % 100 == 0:
                print(f"Counted {message_count} messages...")
            
            # Check if we've reached the expected count
            if message_count >= expected_count:
                break
            
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                print(f"WARNING: Timeout reached after {timeout_seconds} seconds")
                break
        
        consumer.close()
        
        # Verify count
        print("\n" + "="*50)
        print(f"Expected messages: {expected_count}")
        print(f"Actual messages:   {message_count}")
        print("="*50)
        
        if message_count == expected_count:
            print("PASS")
            return True
        else:
            print("FAIL")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to verify messages: {e}")
        return False


def main():
    """Run verification and exit with appropriate code."""
    success = verify_message_count()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
