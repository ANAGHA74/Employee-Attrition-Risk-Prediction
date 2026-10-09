# Hadoop HDFS Storage & Kafka Integration Module

**Person 2 Module: Distributed Storage, Kafka Ingestion & ML Export**  
**Project:** Employee Attrition Risk Prediction Using Big Data Analytics  
**Course:** Big Data Analytics (CSE), Dayananda Sagar College of Engineering  

---

## 1. Architecture Overview

```
+-------------------------------------------------------------+
| 1. Data Ingestion (Person 1)                                |
|    - Source: data/processed/employees_clean.csv (IBM HR)    |
|    - Kafka Producer: kafka_pipeline/producer.py             |
|    - Topic: employee-data (Port 9092)                       |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 2. Distributed Storage & Pipeline (Person 2 - This Module)  |
|    - Kafka-to-HDFS Consumer: hdfs/kafka_hdfs_consumer.py    |
|    - Hadoop HDFS: Single-Node NameNode (9870) + DataNode     |
|    - Storage Location: /user/hr_attrition/raw/batch_*.jsonl  |
|    - Reliability: At-Least-Once, Offset commit on write,     |
|                   Dead-Letter Queue (data/dlq/) spooling    |
|    - Export Utility: hdfs/export_hdfs_data.py               |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
| 3. Risk Prediction & Inference (Person 3)                   |
|    - Model: ml/models/attrition_model.pkl (Scikit-Learn)    |
|    - Predict Script: ml/predict.py                          |
|    - HR Action Threshold: Probability >= 0.60 (HIGH RISK)  |
|    - Output: ml/results/hdfs_employee_risk_predictions.csv  |
+-------------------------------------------------------------+
```

---

## 2. Directory & Component Structure

```
hdfs/
├── README.md               # Complete setup, execution and integration guide
├── core-site.xml           # Hadoop core configuration (fs.defaultFS)
├── hdfs-site.xml           # HDFS site configuration (WebHDFS, replication)
├── hdfs_utils.py           # WebHDFS client, batch writer, DLQ spooling
├── kafka_hdfs_consumer.py  # Kafka consumer writing JSON Lines batches to HDFS
├── export_hdfs_data.py     # HDFS batch consolidation & ML inference bridge
├── test_hdfs.py            # Automated 7-step test suite
└── requirements.txt        # Python dependencies
```

---

## 3. Prerequisites & Environment

- **Operating System:** Windows 10/11, macOS, or Linux
- **Docker Desktop:** Running (provides Kafka, Kafka UI, Hadoop NameNode, DataNode)
- **Python:** 3.10+ with packages in `requirements.txt`

### Port Mappings
| Service | Port | Description |
| :--- | :--- | :--- |
| **Kafka Broker** | `9092` | Apache Kafka plaintext listener |
| **Kafka UI** | `8080` | Web interface: `http://localhost:8080` |
| **HDFS NameNode (WebHDFS)** | `9870` | WebHDFS REST API & UI: `http://localhost:9870` |
| **HDFS NameNode (IPC)** | `9000` | Hadoop RPC communication port |
| **HDFS DataNode (HTTP)** | `9864` | Data block transfer / WebHDFS data streams |

---

## 4. Quick Start & Execution Guide

### Step 1: Start Docker Services
Start Kafka and Hadoop HDFS services together:
```powershell
docker compose up -d
```

Verify that all containers are healthy:
```powershell
docker compose ps
```

Create the Kafka topic (if not already created):
```powershell
docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --topic employee-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
```

### Step 2: Initialize HDFS Directory Structure
Run the directory setup script:
```powershell
python -c "import sys; sys.path.insert(0, 'hdfs'); from hdfs_utils import setup_hdfs_directories; setup_hdfs_directories()"
```
This initializes:
- `/user/hr_attrition/raw/` — Incoming streaming batches from Kafka
- `/user/hr_attrition/processed/` — Exported/staged analytics data
- `/user/hr_attrition/archive/` — Historical processed records

### Step 3: Run the Kafka-to-HDFS Consumer
Open a terminal and start the consumer:
```powershell
python hdfs/kafka_hdfs_consumer.py --batch-size 50
```
*Options:*
- `--batch-size 50` : Flush every 50 employee records to HDFS (default 100)
- `--group-id <name>` : Custom consumer group ID (default `hr-hdfs-consumer-group`)
- `--format jsonl` : Storage format (`jsonl` or `csv`)

*(Alternatively, Person 1's `python kafka_pipeline/consumer.py` also writes to HDFS via `flush_batch` integration).*

### Step 4: Stream Data via Kafka Producer (Person 1)
In a second terminal, send employee records:
```powershell
# Send 100 sample records
python kafka_pipeline/producer.py --delay 0.01 --limit 100

# Or stream the complete dataset of 1470 employees
python kafka_pipeline/producer.py --delay 0.01
```

### Step 5: Export from HDFS and Run ML Predictions (Person 3)
Export stored batches from HDFS to a consolidated CSV and generate attrition risk predictions:
```powershell
python hdfs/export_hdfs_data.py --predict
```
- Consolidated dataset saved to: `data/processed/hdfs_exported_employees.csv`
- Model risk predictions saved to: `ml/results/hdfs_employee_risk_predictions.csv`

---

## 5. Storage Reliability & Delivery Guarantees

1. **At-Least-Once Processing**:
   - `enable_auto_commit=False` in Kafka consumer.
   - Kafka offsets are committed **only after** the batch write to HDFS is acknowledged with HTTP 200/201.
   - If the consumer crashes before HDFS confirms storage, messages will be re-delivered upon restart.

2. **Deduplication Strategy**:
   - `hdfs/export_hdfs_data.py` deduplicates records by `EmployeeNumber` using the ISO-8601 `event_timestamp`, ensuring downstream ML models only receive the latest valid state.

3. **Dead-Letter Queue (DLQ) & Spooling**:
   - If HDFS is temporarily unreachable, batches are automatically spooled to `data/dlq/batch_*.jsonl` locally.
   - When HDFS recovers, `replay_dlq_to_hdfs()` automatically replays and flushes the spooled batches to HDFS.

---

## 6. Automated Test Suite

Run the full 7-step test suite:
```powershell
python hdfs/test_hdfs.py
```

### What the Tests Verify:
- **Test 1 (Health)**: Validates NameNode and WebHDFS endpoints on port 9870.
- **Test 2 (Directory Structure)**: Verifies `/user/hr_attrition/` subdirectories (`raw`, `processed`, `archive`).
- **Test 3 (Write/Read)**: Performs an end-to-end JSON Lines write and read verification on HDFS.
- **Test 4 (Kafka Integration)**: Sends records to Kafka and verifies consumer batching into HDFS.
- **Test 5 (Persistence & Integrity)**: Validates schema and column retention in HDFS files.
- **Test 6 (Restart Behavior)**: Confirms new batches use unique timestamped IDs without overwriting existing files.
- **Test 7 (ML Compatibility)**: Exports from HDFS and validates inference against Person 3's pre-trained model.

---

## 7. Inspecting HDFS Storage

### Via Web Browser
- **HDFS NameNode Web UI**: [http://localhost:9870](http://localhost:9870)
  - Navigate to: *Utilities* -> *Browse the file system* -> `/user/hr_attrition/raw`
- **Kafka UI**: [http://localhost:8080](http://localhost:8080)

### Via Docker CLI
```powershell
# List HDFS files
docker exec namenode hdfs dfs -ls -R /user/hr_attrition

# View contents of an HDFS file
docker exec namenode hdfs dfs -cat /user/hr_attrition/raw/<batch_filename>.jsonl
```

### Via Python API
```python
import sys
sys.path.insert(0, "hdfs")
from hdfs_utils import list_hdfs_directory, read_hdfs_file

# List raw directory
files = list_hdfs_directory("/user/hr_attrition/raw")
for f in files:
    print(f["pathSuffix"], f["length"], "bytes")
```

---

## 8. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Cannot connect to HDFS at localhost:9870` | Docker container not running | Run `docker compose up -d` and verify `docker compose ps` |
| `Topic employee-data not found` | Kafka topic not yet initialized | Run the `kafka-topics.sh --create` command in Step 1 |
| `ValueError: Invalid file descriptor: -1` | Windows IPv6 socket binding | Use `127.0.0.1:9092` instead of `localhost` (configured automatically in `kafka_hdfs_consumer.py`) |
| `DLQ spooled files present` | HDFS was down during consumer execution | Run `python -c "import sys; sys.path.insert(0, 'hdfs'); from hdfs_utils import replay_dlq_to_hdfs; replay_dlq_to_hdfs()"` |
