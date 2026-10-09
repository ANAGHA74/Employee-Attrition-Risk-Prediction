"""
Kafka-to-HDFS Consumer for HR Employee Attrition Data.
Consumes employee records from Apache Kafka topic 'employee-data',
buffers them in configurable batches, writes them reliably to Hadoop HDFS,
and commits Kafka offsets ONLY after successful HDFS persistence (At-Least-Once delivery).
"""

import os
import sys
import json
import time
import signal
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import selectors
import kafka
from kafka import KafkaConsumer, TopicPartition, OffsetAndMetadata
from dotenv import load_dotenv

# Windows Python SelectSelector patch for closed socket descriptor safety
if hasattr(selectors, "SelectSelector"):
    _orig_unregister = selectors.SelectSelector.unregister
    def _safe_unregister(self, fileobj):
        try:
            return _orig_unregister(self, fileobj)
        except (ValueError, KeyError):
            for k, v in list(getattr(self, "_fd_to_key", {}).items()):
                if v.fileobj is fileobj:
                    return self._fd_to_key.pop(k, None)
            return None
    selectors.SelectSelector.unregister = _safe_unregister

# Add project root and hdfs directory to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "hdfs"))
sys.path.insert(0, str(PROJECT_ROOT / "kafka_pipeline"))

from hdfs_utils import (
    check_hdfs_connection,
    setup_hdfs_directories,
    write_batch_to_hdfs,
    replay_dlq_to_hdfs,
    HDFS_RAW_DIR
)
import config as kafka_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("KafkaHDFSConsumer")

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle termination signals cleanly."""
    global running
    logger.info("Shutdown signal (%s) received. Initiating graceful shutdown...", signum)
    running = False


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def validate_employee_record(record: Any) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Validate that the incoming message is a dictionary containing required employee fields.
    
    Returns:
        Tuple[bool, record, error_message]
    """
    if not isinstance(record, dict):
        return False, None, "Message is not a JSON object/dict"
        
    if "EmployeeNumber" not in record:
        return False, None, "Missing 'EmployeeNumber' field"
        
    return True, record, ""


def run_kafka_to_hdfs_pipeline(
    bootstrap_servers: str = None,
    topic: str = None,
    group_id: str = "hr-hdfs-consumer-group",
    batch_size: int = 100,
    hdfs_dir: str = HDFS_RAW_DIR,
    file_format: str = "jsonl",
    auto_offset_reset: str = "earliest",
    max_records: Optional[int] = None,
    flush_interval: float = 2.0
) -> Dict[str, Any]:
    """
    Run the main Kafka-to-HDFS consumer pipeline.
    
    Args:
        bootstrap_servers: Kafka broker address (default from config)
        topic: Topic name (default 'employee-data')
        group_id: Kafka consumer group ID
        batch_size: Number of records per HDFS batch file
        hdfs_dir: Destination HDFS directory
        file_format: 'jsonl' or 'csv'
        auto_offset_reset: 'earliest' or 'latest'
        max_records: Stop after consuming this many records (useful for testing)
        flush_interval: Max idle seconds before flushing pending buffer to HDFS
        
    Returns:
        Summary dict of processed records and batches.
    """
    global running
    running = True
    raw_servers = bootstrap_servers or getattr(kafka_config, "BOOTSTRAP_SERVERS", "127.0.0.1:9092")
    servers = raw_servers.replace("localhost", "127.0.0.1")
    topic_name = topic or getattr(kafka_config, "TOPIC", "employee-data")
    
    logger.info("=" * 65)
    logger.info("STARTING KAFKA -> HDFS INGESTION PIPELINE")
    logger.info("=" * 65)
    logger.info("Kafka Broker        : %s", servers)
    logger.info("Topic               : %s", topic_name)
    logger.info("Consumer Group      : %s", group_id)
    logger.info("Offset Reset        : %s", auto_offset_reset)
    logger.info("Batch Size          : %d", batch_size)
    logger.info("HDFS Destination    : %s", hdfs_dir)
    logger.info("Storage Format      : %s", file_format)
    logger.info("=" * 65)
    
    # 1. Verify HDFS status and ensure directories exist
    hdfs_available = check_hdfs_connection()
    if hdfs_available:
        setup_hdfs_directories()
        replayed_stats = replay_dlq_to_hdfs()
        if replayed_stats.get("replayed_batches", 0) > 0:
            logger.info(
                "Replayed %d DLQ batch(es) (%d records) to HDFS.",
                replayed_stats["replayed_batches"],
                replayed_stats["replayed_records"]
            )
    else:
        logger.warning("HDFS is not currently reachable! Records will be safely spooled to local DLQ.")
        
    # 2. Create Kafka Consumer with manual offset commits
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=servers,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=False,  # Manual commit ONLY after HDFS write
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        key_deserializer=lambda m: m.decode("utf-8") if m else None,
        consumer_timeout_ms=1000
    )
    
    buffer: List[Dict[str, Any]] = []
    buffer_partition_offsets: Dict[TopicPartition, int] = {}
    batch_counter = 0
    total_consumed = 0
    total_persisted_hdfs = 0
    total_spooled_dlq = 0
    malformed_count = 0
    written_files: List[str] = []
    
    def flush_and_commit() -> bool:
        nonlocal batch_counter, total_persisted_hdfs, total_spooled_dlq
        if not buffer:
            return True
            
        batch_counter += 1
        batch_id = f"batch_{int(time.time())}_{batch_counter:04d}"
        logger.info(
            "Writing batch #%d (%d records) to HDFS...",
            batch_counter, len(buffer)
        )
        
        success, location = write_batch_to_hdfs(
            records=buffer,
            destination_dir=hdfs_dir,
            file_format=file_format,
            batch_id=batch_id
        )
        
        if success:
            logger.info("Persisted batch #%d (%d records) to HDFS: %s", batch_counter, len(buffer), location)
            written_files.append(location)
            total_persisted_hdfs += len(buffer)
            
            # Commit exact offsets only for the records safely persisted in this batch
            if buffer_partition_offsets:
                exact_offsets = {
                    tp: OffsetAndMetadata(offset + 1, "")
                    for tp, offset in buffer_partition_offsets.items()
                }
                try:
                    consumer.commit(offsets=exact_offsets)
                    logger.info("Committed exact Kafka offsets for batch #%d: %s", batch_counter, exact_offsets)
                except Exception as e:
                    logger.warning("Failed to commit exact offsets to Kafka: %s", e)
        else:
            logger.warning("HDFS write failed. Batch (%d records) safely spooled to local DLQ: %s", len(buffer), location)
            total_spooled_dlq += len(buffer)
            # DO NOT commit Kafka offsets for failed batches to guarantee At-Least-Once delivery
            
        buffer.clear()
        buffer_partition_offsets.clear()
        return success

    last_record_time = time.time()
    flush_interval = 2.0  # Flush pending buffer if no new messages arrive for 2 seconds

    logger.info("Consumer listening for messages... (Press Ctrl+C to stop)")
    
    try:
        while running:
            # Poll for messages
            raw_batches = consumer.poll(timeout_ms=1000)
            
            if raw_batches:
                for topic_partition, messages in raw_batches.items():
                    for message in messages:
                        if not running:
                            break
                            
                        raw_val = message.value
                        is_valid, record, err_msg = validate_employee_record(raw_val)
                        
                        if not is_valid:
                            logger.warning(
                                "Malformed record at offset %d: %s. Raw: %s",
                                message.offset, err_msg, raw_val
                            )
                            malformed_count += 1
                            continue
                            
                        buffer.append(record)
                        last_record_time = time.time()
                        tp = TopicPartition(message.topic, message.partition)
                        if tp not in buffer_partition_offsets or message.offset > buffer_partition_offsets[tp]:
                            buffer_partition_offsets[tp] = message.offset
                            
                        total_consumed += 1
                        
                        if len(buffer) >= batch_size:
                            flush_and_commit()
                            
                        if max_records and total_consumed >= max_records:
                            logger.info("Reached target limit of %d records. Stopping.", max_records)
                            running = False
                            break
            else:
                # Idle poll: check if pending buffer has timed out
                if buffer and (time.time() - last_record_time >= flush_interval):
                    logger.info(
                        "Flushing %d pending record(s) due to idle timeout (%.1fs)...",
                        len(buffer), flush_interval
                    )
                    flush_and_commit()
                        
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt caught.")
    except Exception as e:
        logger.error("Consumer loop encountered error: %s", e, exc_info=True)
    finally:
        # Flush any remaining buffer on exit
        if buffer:
            logger.info("Flushing final buffer batch of %d records...", len(buffer))
            flush_and_commit()
            
        consumer.close()
        logger.info("Kafka consumer closed.")
        
    summary = {
        "total_consumed": total_consumed,
        "total_persisted_hdfs": total_persisted_hdfs,
        "total_spooled_dlq": total_spooled_dlq,
        "malformed_count": malformed_count,
        "total_batches": batch_counter,
        "files_written": written_files
    }
    
    logger.info("=" * 65)
    logger.info("CONSUMER SUMMARY")
    logger.info("=" * 65)
    logger.info("Total Consumed       : %d", total_consumed)
    logger.info("Persisted to HDFS    : %d", total_persisted_hdfs)
    logger.info("Spooled to DLQ       : %d", total_spooled_dlq)
    logger.info("Malformed Dropped    : %d", malformed_count)
    logger.info("Total Batches        : %d", batch_counter)
    logger.info("Files Written        : %d", len(written_files))
    logger.info("=" * 65)
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Consume Kafka employee records and store in HDFS")
    parser.add_argument("--batch-size", type=int, default=100, help="Records per HDFS batch (default: 100)")
    parser.add_argument("--group-id", type=str, default="hr-hdfs-consumer-group", help="Kafka Consumer Group ID")
    parser.add_argument("--format", type=str, choices=["jsonl", "csv"], default="jsonl", help="Storage format (default: jsonl)")
    parser.add_argument("--limit", type=int, default=None, help="Max records to consume (for testing)")
    parser.add_argument("--offset-reset", type=str, choices=["earliest", "latest"], default="earliest", help="Auto offset reset")
    parser.add_argument("--flush-interval", type=float, default=2.0, help="Max idle seconds before buffer flush (default: 2.0)")
    
    args = parser.parse_args()
    
    run_kafka_to_hdfs_pipeline(
        batch_size=args.batch_size,
        group_id=args.group_id,
        file_format=args.format,
        max_records=args.limit,
        auto_offset_reset=args.offset_reset,
        flush_interval=args.flush_interval
    )


if __name__ == "__main__":
    main()
