# Kafka Data Ingestion - Employee Attrition Risk Prediction

This is the Kafka data ingestion component of the Employee Attrition Risk Prediction Big Data pipeline. It handles loading the HR dataset, streaming it through Kafka, and preparing it for downstream HDFS storage.

## Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│   IBM HR CSV    │─────▶│   Producer   │─────▶│ Kafka Topic │─────▶│ Consumer │
│ (raw data)      │      │  (send data) │      │employee-data│      │(receive) │
└─────────────────┘      └──────────────┘      └─────────────┘      └────┬─────┘
                                                                               │
                                                                               ▼
                                                                        ┌──────────┐
                                                                        │   HDFS   │
                                                                        │ (Person 2)│
                                                                        └──────────┘
```

## Setup Instructions (PowerShell)

### 1. Create Project Structure

```powershell
mkdir data\raw, data\processed, kafka_pipeline
```

### 2. Place Dataset

Copy `WA_Fn-UseC_-HR-Employee-Attrition.csv` to `data\raw\` folder.

### 3. Start Kafka with Docker

```powershell
docker compose up -d
```

Verify containers are running:
```powershell
docker ps
```

### 4. Create Kafka Topic

```powershell
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic employee-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### 5. Set Up Python Environment

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 6. (Optional) Configure Environment Variables

Copy `.env.example` to `.env` and modify if needed:
```powershell
copy .env.example .env
```

The pipeline works without `.env` file (uses defaults). See `.env.example` for available settings.

### 7. Preprocess Data

```powershell
python preprocess.py
```

This creates `data\processed\employees_clean.csv` with constant columns removed.

## Usage

### Run Producer (Send Data to Kafka)

```powershell
# From project root
python kafka_pipeline\producer.py

# With custom delay between messages (seconds)
python kafka_pipeline\producer.py --delay 0.5

# Limit to first 100 records (for testing)
python kafka_pipeline\producer.py --limit 100
```

### Run Consumer (Receive Data from Kafka)

```powershell
# From project root
python kafka_pipeline\consumer.py
```

Press `Ctrl+C` to stop gracefully. The consumer buffers records in batches of 100 and calls `flush_batch()` for HDFS storage (Person 2's responsibility).

**To replay from the beginning** (use a new consumer group):
```powershell
$env:GROUP_ID="new-consumer-group"
python kafka_pipeline\consumer.py
```

### Verify Message Count

```powershell
python verify.py
```

This reads the CSV row count and compares it to the Kafka topic message count. Prints PASS or FAIL.

## JSON Message Schema

Each message sent to Kafka is a JSON object with the following fields:

```json
{
  "Age": 41,
  "Attrition": "Yes",
  "BusinessTravel": "Travel_Rarely",
  "DailyRate": 1102,
  "Department": "Sales",
  "DistanceFromHome": 1,
  "Education": 2,
  "EducationField": "Life Sciences",
  "EmployeeNumber": 1,
  "EnvironmentSatisfaction": 2,
  "Gender": "Female",
  "HourlyRate": 94,
  "JobInvolvement": 3,
  "JobLevel": 2,
  "JobRole": "Sales Executive",
  "JobSatisfaction": 4,
  "MaritalStatus": "Single",
  "MonthlyIncome": 5993,
  "MonthlyRate": 19479,
  "NumCompaniesWorked": 8,
  "OverTime": "Yes",
  "PercentSalaryHike": 11,
  "PerformanceRating": 3,
  "RelationshipSatisfaction": 1,
  "StockOptionLevel": 0,
  "TotalWorkingYears": 8,
  "TrainingTimesLastYear": 0,
  "WorkLifeBalance": 1,
  "YearsAtCompany": 6,
  "YearsInCurrentRole": 4,
  "YearsSinceLastPromotion": 0,
  "YearsWithCurrManager": 5,
  "event_timestamp": "2026-10-08T10:30:45.123456+00:00"
}
```

**Notes:**
- `EmployeeNumber` is used as the message key (enables partitioning by employee)
- `event_timestamp` is added by the producer in ISO 8601 format (UTC)
- Numeric columns are sent as JSON numbers (e.g., `"Age": 41`, not `"Age": "41"`)
- Text columns are sent as strings
- Constant columns removed: `EmployeeCount`, `StandardHours`, `Over18`

## Verify Messages in Kafka UI

1. Open Kafka UI at http://localhost:8080
2. Click on the "local" cluster
3. Navigate to Topics → employee-data
4. Click the "Messages" tab
5. You can view individual messages, filter by key (EmployeeNumber), or export

## Troubleshooting

### NoBrokersAvailable Error

**Problem:** `kafka.errors.NoBrokersAvailable: No available brokers`  
**Cause:** Kafka broker is not running or not accessible  
**Solution:**
- Check Docker: `docker ps` - ensure kafka container is running
- Check Kafka logs: `docker logs kafka`
- Verify bootstrap server address in `kafka_pipeline/config.py` (default: `localhost:9092`)

### Port Conflicts

**Problem:** Kafka fails to start due to port 9092 or 9093 already in use  
**Solution:**
- Check what's using the port: `netstat -ano | findstr :9092`
- Stop conflicting service or change ports in `docker-compose.yml`

### Advertised Listeners Issue

**Problem:** Producer cannot connect to Kafka from host machine  
**Cause:** Kafka's `KAFKA_ADVERTISED_LISTENERS` misconfigured  
**Solution:**
- Ensure `docker-compose.yml` has: `PLAINTEXT://localhost:9092`
- Restart Kafka: `docker compose down && docker compose up -d`

### Docker Not Running

**Problem:** `docker compose up` fails with connection errors  
**Cause:** Docker Desktop is not running  
**Solution:**
- Start Docker Desktop application
- Wait for it to fully initialize (check Docker icon in system tray)
- Retry: `docker compose up -d`

### Topic Already Exists

**Problem:** Topic creation fails with "Topic 'employee-data' already exists"  
**Solution:**
- This is normal if you already created the topic
- To delete and recreate (WARNING: deletes all messages):
  ```powershell
  docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --delete --topic employee-data --bootstrap-server localhost:9092
  docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic employee-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
  ```

### Consumer Not Receiving Messages

**Problem:** Consumer starts but receives no messages  
**Cause:** Consumer group offset already at end of topic  
**Solution:**
- Use a different GROUP_ID:
  ```powershell
  $env:GROUP_ID="new-consumer-group"
  python kafka_pipeline\consumer.py
  ```
- Or reset offsets for existing group:
  ```powershell
  docker exec -it kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group hr-consumer-group --reset-offsets --to-earliest --topic employee-data --execute
  ```

## File Structure

```
bda_project/
├── data/
│   ├── raw/
│   │   └── WA_Fn-UseC_-HR-Employee-Attrition.csv  (original dataset)
│   └── processed/
│       └── employees_clean.csv                    (cleaned dataset)
├── kafka_pipeline/
│   ├── config.py                                  (configuration)
│   ├── producer.py                                (Kafka producer)
│   └── consumer.py                                (Kafka consumer)
├── docker-compose.yml                             (Kafka + Kafka UI)
├── preprocess.py                                  (data cleaning)
├── verify.py                                      (message count verification)
├── requirements.txt                               (Python dependencies)
├── .env.example                                   (environment variable template)
├── .gitignore                                     (git ignore rules)
└── README.md                                      (this file)
```

## Dependencies

- `pandas==3.0.0` - CSV data handling
- `kafka-python-ng==2.2.3` - Kafka client library
- `python-dotenv==1.0.0` - Environment variable support (optional, uses defaults if not present)

## Team Integration

- **Person 1 (me):** Kafka data ingestion (this component)
- **Person 2:** HDFS storage - implement `flush_batch()` in `kafka_pipeline/consumer.py`
- **Person 3:** ML model - consumes from HDFS, trains attrition risk model
- **Person 4:** Streamlit dashboard - displays risk scores for HR review

## How to Continue (for Teammates)

The Kafka ingestion module is **complete and verified** (run `python verify.py` - should print PASS).

### Person 2: HDFS Storage
- Implement the HDFS write logic inside `flush_batch(records: list[dict])` in `kafka_pipeline/consumer.py`
- Keep HDFS-specific code in a separate module (e.g., `hdfs/hdfs_utils.py`)
- The function receives a list of employee records (each is a dict matching the JSON schema)
- Clear the buffer after successful write
- Handle write failures gracefully
- **Do not change:** the function signature `flush_batch(records: list)`

### Person 3: ML Model
- Train the attrition risk model on `data/processed/employees_clean.csv`
- Write predictions as a file with columns: `EmployeeNumber`, `risk_score` (0-1), `risk_level` (High/Medium/Low based on threshold >= 0.6)
- Use the existing message fields from Kafka (via HDFS) for features

### Person 4: Streamlit Dashboard
- Build a dashboard to read the predictions file
- Display employee risk scores and flag high-risk employees for HR review
- Integrate with the ML model output

### Important Constraints
- **Do not change:** topic name `employee-data`
- **Do not change:** the message field names or structure
- **Do not change:** the `flush_batch(records: list)` signature
