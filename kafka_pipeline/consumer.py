"""
Kafka consumer for HR Employee Attrition data.
Consumes messages from Kafka topic and buffers them for HDFS storage.
"""

import sys
import json

import kafka  # kafka-python-ng package
from kafka import KafkaConsumer

# Import config from the same directory
from config import (
    BOOTSTRAP_SERVERS,
    TOPIC,
    GROUP_ID,
    AUTO_OFFSET_RESET,
    BATCH_SIZE
)


# Global flag for graceful shutdown
running = True


def handle_record(record: dict) -> dict:
    """
    Process a single consumed record.
    Logs the record, counts it, and returns it for buffering.
    
    Args:
        record: The deserialized message value (dict)
    
    Returns:
        The processed record
    """
    employee_id = record.get('EmployeeNumber', 'Unknown')
    timestamp = record.get('event_timestamp', 'Unknown')
    
    print(f"Consumed Employee {employee_id} at {timestamp}")
    
    return record


def flush_batch(records: list):
    """
    Flush a batch of records to storage.
    
    Person 2: Write to HDFS here
    This function should:
    - Write the batch of records to HDFS
    - Clear the buffer after successful write
    - Handle write failures gracefully
    
    Args:
        records: List of employee records to write
    """
    print(f"Flushing batch of {len(records)} records to storage...")
    
    # Placeholder for HDFS write logic
    # Example: from hdfs.hdfs_utils import write_to_hdfs
    #          write_to_hdfs(records, path="/employee_data/batch_x.json")
    
    # Clear the buffer (implementation will depend on HDFS client)
    # records.clear()
    
    print(f"Batch flush complete (stub - waiting for Person 2's HDFS implementation)")


def consume_messages():
    """
    Consume messages from Kafka topic and buffer for HDFS storage.
    """
    # Create Kafka consumer
    print(f"Connecting to Kafka at {BOOTSTRAP_SERVERS}")
    print(f"Topic: {TOPIC}, Group ID: {GROUP_ID}")
    print(f"Auto offset reset: {AUTO_OFFSET_RESET}")
    
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset=AUTO_OFFSET_RESET,
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        key_deserializer=lambda m: m.decode('utf-8') if m else None
    )
    
    # Buffer for batching records
    record_buffer = []
    total_consumed = 0
    
    print("Starting consumer... (Press Ctrl+C to stop)")
    
    try:
        # Polling loop - checks running flag every second
        # Using poll() instead of iterator allows Ctrl+C to exit within ~1 second
        while running:
            # Poll for messages with 1 second timeout
            raw_records = consumer.poll(timeout_ms=1000)
            
            # Process polled messages
            for topic_partition, messages in raw_records.items():
                for message in messages:
                    # Deserialize and handle the record
                    record = message.value
                    processed_record = handle_record(record)
                    
                    # Add to buffer
                    record_buffer.append(processed_record)
                    total_consumed += 1
                    
                    # Flush batch when buffer reaches batch size
                    if len(record_buffer) >= BATCH_SIZE:
                        flush_batch(record_buffer)
                        record_buffer.clear()
        
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    except Exception as e:
        print(f"Error consuming messages: {e}")
    finally:
        # Flush any remaining records in buffer
        if record_buffer:
            print(f"Flushing final batch of {len(record_buffer)} records...")
            flush_batch(record_buffer)
        
        # Close consumer
        consumer.close()
        print(f"Total messages consumed: {total_consumed}")


if __name__ == "__main__":
    consume_messages()
