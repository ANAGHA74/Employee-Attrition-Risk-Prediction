"""
Kafka Console Consumer for HR Employee Attrition Data (Person 1 Component).
Consumes messages from Kafka topic 'employee-data' and displays them on the console.

NOTE FOR HDFS STORAGE:
To persist Kafka batches into Hadoop HDFS with reliable offset management
and DLQ fault tolerance, run the official HDFS consumer:
    python hdfs/kafka_hdfs_consumer.py
"""

import sys
import json
from pathlib import Path

import kafka
from kafka import KafkaConsumer

# Add kafka_pipeline directory to path for config import
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from config import (
    BOOTSTRAP_SERVERS,
    TOPIC,
    GROUP_ID,
    AUTO_OFFSET_RESET,
    BATCH_SIZE
)

# Normalize localhost to 127.0.0.1 for clean Windows socket resolution
SERVERS = BOOTSTRAP_SERVERS.replace("localhost", "127.0.0.1")

# Global flag for graceful shutdown
running = True


def handle_record(record: dict) -> dict:
    """
    Process a single consumed record for console display.
    
    Args:
        record: The deserialized message value (dict)
        
    Returns:
        The processed record
    """
    employee_id = record.get('EmployeeNumber', 'Unknown')
    timestamp = record.get('event_timestamp', 'Unknown')
    dept = record.get('Department', 'N/A')
    role = record.get('JobRole', 'N/A')
    
    print(f"[STREAM] Consumed Employee #{employee_id:<5} | Dept: {dept:<22} | Role: {role:<24} | At: {timestamp}")
    return record


def consume_messages():
    """
    Consume and display messages from Kafka topic for live streaming inspection.
    """
    print("=" * 70)
    print("HR EMPLOYEE DATA - LIVE KAFKA STREAM CONSUMER")
    print("=" * 70)
    print(f"Connecting to Kafka at {SERVERS}")
    print(f"Topic: {TOPIC}, Group ID: {GROUP_ID}")
    print(f"Auto offset reset: {AUTO_OFFSET_RESET}")
    print("Note: For persistent HDFS distributed storage, use 'python hdfs/kafka_hdfs_consumer.py'")
    print("=" * 70)
    
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset=AUTO_OFFSET_RESET,
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        key_deserializer=lambda m: m.decode('utf-8') if m else None,
        consumer_timeout_ms=1000
    )
    
    total_consumed = 0
    print("Starting consumer... (Press Ctrl+C to stop)\n")
    
    try:
        while running:
            raw_records = consumer.poll(timeout_ms=1000)
            for topic_partition, messages in raw_records.items():
                for message in messages:
                    record = message.value
                    handle_record(record)
                    total_consumed += 1
                    
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down...")
    except Exception as e:
        print(f"Error consuming messages: {e}")
    finally:
        consumer.close()
        print("\n" + "=" * 50)
        print(f"Console Consumer Stopped. Total messages viewed: {total_consumed}")
        print("=" * 50)


if __name__ == "__main__":
    consume_messages()
