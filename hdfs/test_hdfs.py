"""
Comprehensive Test Suite for HDFS Storage, Ingestion, Sanitization, and ML Integration.
Verifies all data pipeline stages, schema integrity, deduplication, test-record isolation,
and ML risk prediction inference.
"""

import os
import sys
import json
import time
import unittest
from pathlib import Path

import selectors
import pandas as pd
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

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "hdfs"))
sys.path.insert(0, str(PROJECT_ROOT / "kafka_pipeline"))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from hdfs_utils import (
    check_hdfs_connection,
    create_hdfs_directory,
    setup_hdfs_directories,
    write_batch_to_hdfs,
    read_hdfs_file,
    list_hdfs_directory,
    read_all_records_from_hdfs,
    HDFS_RAW_DIR,
    HDFS_PROCESSED_DIR,
    HDFS_ARCHIVE_DIR
)
from export_hdfs_data import (
    export_hdfs_data,
    run_ml_prediction_on_hdfs_data,
    separate_production_and_test_records,
    CANONICAL_COLUMNS
)
from kafka_hdfs_consumer import run_kafka_to_hdfs_pipeline
import config as kafka_config


class TestHDFSPipeline(unittest.TestCase):
    """Automated Test Suite for HDFS, Kafka Ingestion, and ML Pipeline."""

    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 70)
        print("STARTING HDFS, DATA SANITIZATION & ML TEST SUITE")
        print("=" * 70)

    def test_01_hdfs_health(self):
        """Test 1: HDFS Health - Verify NameNode and WebHDFS reachability."""
        print("\n[TEST 1] Verifying HDFS NameNode and WebHDFS health...")
        is_healthy = check_hdfs_connection()
        self.assertTrue(is_healthy, "HDFS NameNode is not accessible via WebHDFS.")
        
        root_items = list_hdfs_directory("/")
        self.assertIsInstance(root_items, list)
        print(f"PASS: HDFS NameNode is healthy. Root contents: {len(root_items)} item(s)")

    def test_02_directory_creation(self):
        """Test 2: Directory Creation - Ensure standard project HDFS directories exist."""
        print("\n[TEST 2] Verifying HDFS directory structure creation...")
        ok = setup_hdfs_directories()
        self.assertTrue(ok, "Failed to initialize standard HDFS directories.")
        
        items = list_hdfs_directory("/user/hr_attrition")
        suffixes = {item.get("pathSuffix") for item in items}
        self.assertIn("raw", suffixes, "Missing /user/hr_attrition/raw directory")
        self.assertIn("processed", suffixes, "Missing /user/hr_attrition/processed directory")
        self.assertIn("archive", suffixes, "Missing /user/hr_attrition/archive directory")
        print(f"PASS: All HDFS directories exist: {suffixes}")

    def test_03_write_and_read(self):
        """Test 3: Write and Read - Test round-trip persistence of a batch on HDFS."""
        print("\n[TEST 3] Testing HDFS batch write and read roundtrip...")
        test_records = [
            {"EmployeeNumber": 9001, "Age": 29, "Department": "Research & Development", "Attrition": "No", "record_type": "test_synthetic", "is_test": True},
            {"EmployeeNumber": 9002, "Age": 38, "Department": "Sales", "Attrition": "Yes", "record_type": "test_synthetic", "is_test": True}
        ]
        test_batch_id = f"unit_test_batch_{int(time.time())}"
        success, hdfs_path = write_batch_to_hdfs(
            records=test_records,
            destination_dir=HDFS_RAW_DIR,
            file_format="jsonl",
            batch_id=test_batch_id
        )
        self.assertTrue(success, f"Failed to write test batch to HDFS: {hdfs_path}")
        self.assertTrue(hdfs_path.startswith(HDFS_RAW_DIR))
        
        content = read_hdfs_file(hdfs_path)
        self.assertIsNotNone(content, "Failed to read back created HDFS file.")
        lines = [json.loads(l) for l in content.strip().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["EmployeeNumber"], 9001)
        self.assertEqual(lines[1]["EmployeeNumber"], 9002)
        print(f"PASS: Successfully wrote and verified HDFS file at {hdfs_path}")

    def test_04_kafka_integration(self):
        """Test 4: Kafka Integration - Produce records to Kafka and consume into HDFS."""
        print("\n[TEST 4] Testing Kafka-to-HDFS streaming ingestion...")
        from kafka import KafkaProducer
        
        servers = getattr(kafka_config, "BOOTSTRAP_SERVERS", "127.0.0.1:9092").replace("localhost", "127.0.0.1")
        topic = getattr(kafka_config, "TOPIC", "employee-data")
        
        producer = KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: str(k).encode("utf-8")
        )
        
        test_records_count = 15
        for i in range(1, test_records_count + 1):
            emp_id = 8000 + i
            msg = {
                "EmployeeNumber": emp_id,
                "Age": 25 + (i % 20),
                "Department": "Sales" if i % 2 == 0 else "Research & Development",
                "JobRole": "Sales Executive" if i % 2 == 0 else "Research Scientist",
                "MonthlyIncome": 3000 + (i * 200),
                "OverTime": "Yes" if i % 3 == 0 else "No",
                "Attrition": "No",
                "record_type": "test_synthetic",
                "is_test": True,
                "event_timestamp": "2026-10-09T14:00:00Z"
            }
            future = producer.send(topic, key=emp_id, value=msg)
            future.get(timeout=5)
            
        producer.flush()
        producer.close()
        print(f"Produced {test_records_count} test records to Kafka topic '{topic}'")
        
        test_group = f"test-hdfs-consumer-{int(time.time())}"
        summary = run_kafka_to_hdfs_pipeline(
            bootstrap_servers=servers,
            topic=topic,
            group_id=test_group,
            batch_size=10,
            auto_offset_reset="earliest",
            max_records=test_records_count,
            flush_interval=1.0
        )
        
        self.assertGreaterEqual(summary["total_consumed"], test_records_count)
        self.assertGreaterEqual(summary["total_persisted_hdfs"], test_records_count)
        print(f"PASS: Consumed {summary['total_consumed']} records from Kafka and wrote to HDFS batches.")

    def test_05_persistence_and_integrity(self):
        """Test 5: Persistence - Verify stored records in HDFS match expected schema."""
        print("\n[TEST 5] Testing record persistence and schema integrity in HDFS...")
        all_records = read_all_records_from_hdfs(HDFS_RAW_DIR)
        self.assertGreater(len(all_records), 0, "No records found in HDFS raw directory.")
        
        sample = all_records[0]
        self.assertIn("EmployeeNumber", sample, "Missing EmployeeNumber in stored record.")
        print(f"PASS: Read {len(all_records)} total records from HDFS. Sample fields: {list(sample.keys())[:6]}")

    def test_06_restart_behavior(self):
        """Test 6: Restart Behavior - Verify existing batches are not overwritten on restart."""
        print("\n[TEST 6] Testing consumer restart behavior and file uniqueness...")
        files_before = list_hdfs_directory(HDFS_RAW_DIR)
        count_before = len([f for f in files_before if f.get("type") == "FILE"])
        
        records = [{"EmployeeNumber": 9999, "Age": 45, "OverTime": "No", "record_type": "test_synthetic", "is_test": True}]
        ok, path = write_batch_to_hdfs(records, destination_dir=HDFS_RAW_DIR)
        self.assertTrue(ok)
        
        files_after = list_hdfs_directory(HDFS_RAW_DIR)
        count_after = len([f for f in files_after if f.get("type") == "FILE"])
        
        self.assertEqual(count_after, count_before + 1, "New batch did not increment file count.")
        print(f"PASS: Batch file count increased from {count_before} to {count_after} without overwriting previous data.")

    def test_07_ml_compatibility(self):
        """Test 7: ML Compatibility - Verify Person 3's ML prediction runs on clean schema."""
        print("\n[TEST 7] Testing ML model inference compatibility...")
        from predict import load_model, predict_employee
        model = load_model()
        self.assertIsNotNone(model)
        
        clean_csv = PROJECT_ROOT / "data" / "processed" / "employees_clean.csv"
        self.assertTrue(clean_csv.exists(), "employees_clean.csv missing")
        test_df = pd.read_csv(clean_csv).head(20)
        predictions = predict_employee(model, test_df)
        self.assertEqual(len(predictions), 20)
        self.assertIn("AttritionProbability", predictions.columns)
        self.assertIn("RiskLevel", predictions.columns)
        self.assertIn("HRReview", predictions.columns)
        print("PASS: Person 3's ML inference executed successfully on data schema.")

    def test_08_dlq_spool_and_replay(self):
        """Test 8: Dead-Letter Queue (DLQ) Spooling and Replay Recovery."""
        print("\n[TEST 8] Testing DLQ spooling and replay recovery...")
        from hdfs_utils import LOCAL_DLQ_DIR, replay_dlq_to_hdfs
        
        LOCAL_DLQ_DIR.mkdir(parents=True, exist_ok=True)
        test_dlq_file = LOCAL_DLQ_DIR / f"test_dlq_batch_{int(time.time())}.jsonl"
        test_data = json.dumps({"EmployeeNumber": 7777, "Age": 33, "Department": "Sales", "record_type": "test_synthetic", "is_test": True}) + "\n"
        with open(test_dlq_file, "w") as f:
            f.write(test_data)
        self.assertTrue(test_dlq_file.exists(), "Failed to create local DLQ test file.")
        
        stats = replay_dlq_to_hdfs()
        self.assertGreaterEqual(stats["replayed_batches"], 1, "DLQ replay did not process batch.")
        self.assertFalse(test_dlq_file.exists(), "Replayed DLQ file was not cleared after persistence.")
        print(f"PASS: Replayed {stats['replayed_batches']} DLQ batch(es) ({stats['replayed_records']} records) to HDFS.")

    def test_09_source_dataset_integrity(self):
        """Test 9: Source Dataset Integrity - Verify source datasets have exactly 1,470 records."""
        print("\n[TEST 9] Verifying source dataset row counts and unique IDs...")
        raw_csv = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
        clean_csv = PROJECT_ROOT / "data" / "processed" / "employees_clean.csv"
        
        raw_df = pd.read_csv(raw_csv)
        clean_df = pd.read_csv(clean_csv)
        
        self.assertEqual(len(raw_df), 1470, f"Raw IBM HR dataset row count is {len(raw_df)}, expected 1470")
        self.assertEqual(raw_df["EmployeeNumber"].nunique(), 1470, "Raw dataset unique EmployeeNumbers != 1470")
        
        self.assertEqual(len(clean_df), 1470, f"Clean dataset row count is {len(clean_df)}, expected 1470")
        self.assertEqual(clean_df["EmployeeNumber"].nunique(), 1470, "Clean dataset unique EmployeeNumbers != 1470")
        print("PASS: Verified source dataset contains exactly 1,470 unique employee records.")

    def test_10_test_isolation_and_deduplication(self):
        """Test 10: Test Isolation & Deduplication - Verify test records are segregated."""
        print("\n[TEST 10] Testing test record isolation and deduplication logic...")
        export_csv_path = PROJECT_ROOT / "data" / "processed" / "hdfs_test_prod_export.csv"
        test_csv_path = PROJECT_ROOT / "data" / "processed" / "hdfs_test_isolated_export.csv"
        
        prod_df, test_df = export_hdfs_data(
            source_dir=HDFS_RAW_DIR,
            output_path=export_csv_path,
            test_output_path=test_csv_path,
            deduplicate=True,
            isolate_tests=True
        )
        
        self.assertEqual(len(prod_df), 1470, f"Expected exactly 1470 production records, got {len(prod_df)}")
        self.assertEqual(prod_df["EmployeeNumber"].nunique(), 1470, "Production records do not have 1470 unique IDs")
        self.assertGreater(len(test_df), 0, "No test records were isolated")
        
        # Verify no test ID exists in production export
        test_ids = set(test_df["EmployeeNumber"])
        prod_ids = set(prod_df["EmployeeNumber"])
        overlap = prod_ids.intersection(test_ids)
        self.assertEqual(len(overlap), 0, f"Found test records in production export: {overlap}")
        print(f"PASS: Isolated {len(test_df)} test records. Clean production dataset contains exactly 1,470 records.")

    def test_11_ml_predictions_generation(self):
        """Test 11: Prediction Generation - Verify predictions generated for all 1,470 employees."""
        print("\n[TEST 11] Testing full prediction generation on clean exported records...")
        clean_export_path = PROJECT_ROOT / "data" / "processed" / "hdfs_exported_employees.csv"
        prod_df, _ = export_hdfs_data(
            source_dir=HDFS_RAW_DIR,
            output_path=clean_export_path,
            deduplicate=True,
            isolate_tests=True
        )
        
        pred_output_path = PROJECT_ROOT / "ml" / "results" / "hdfs_test_predictions.csv"
        predictions = run_ml_prediction_on_hdfs_data(
            exported_df=prod_df,
            output_prediction_path=pred_output_path
        )
        
        self.assertEqual(len(predictions), 1470, f"Expected 1470 predictions, got {len(predictions)}")
        self.assertIn("EmployeeNumber", predictions.columns)
        self.assertIn("AttritionProbability", predictions.columns)
        self.assertIn("RiskLevel", predictions.columns)
        self.assertIn("HRReview", predictions.columns)
        
        # Verify risk levels are valid
        valid_risks = {"LOW", "MEDIUM", "HIGH"}
        actual_risks = set(predictions["RiskLevel"].unique())
        self.assertTrue(actual_risks.issubset(valid_risks), f"Unexpected risk levels: {actual_risks}")
        print(f"PASS: Generated 1,470 risk predictions. Distribution: {predictions['RiskLevel'].value_counts().to_dict()}")

    def test_12_repeatable_export(self):
        """Test 12: Repeatability - Verify multiple export runs produce identical results."""
        print("\n[TEST 12] Testing export repeatability and idempotency...")
        export_1, _ = export_hdfs_data(source_dir=HDFS_RAW_DIR, deduplicate=True, isolate_tests=True)
        export_2, _ = export_hdfs_data(source_dir=HDFS_RAW_DIR, deduplicate=True, isolate_tests=True)
        
        self.assertEqual(len(export_1), len(export_2))
        self.assertTrue(export_1["EmployeeNumber"].equals(export_2["EmployeeNumber"]))
        print("PASS: Export pipeline is idempotent and repeatable.")


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHDFSPipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
