# Employee Attrition Risk Prediction

A Big Data Analytics pipeline that estimates how likely each employee is to leave a company, enabling HR teams to intervene proactively **before** someone resigns.

---

## 1. Problem Statement

HR teams typically discover an employee is leaving only when a resignation letter arrives, which is too late for retention. This project ingests streaming employee data, stores it in distributed Hadoop HDFS batches, evaluates attrition likelihood with a trained Machine Learning model, and flags any employee with a risk score of **0.60 or higher** for immediate HR review on an interactive dashboard.

---

## 2. Architecture & Data Flow

```
+---------------------------------------------------------------------------------+
| 1. Data Ingestion (Kafka)                                                       |
|    - Dataset: data/processed/employees_clean.csv (IBM HR 1470 records)          |
|    - Producer: kafka_pipeline/producer.py -> Topic: employee-data:9092          |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 2. Distributed Storage (Hadoop HDFS)                                            |
|    - Official Consumer: hdfs/kafka_hdfs_consumer.py                             |
|    - Target HDFS Path: /user/hr_attrition/raw/batch_*.jsonl                     |
|    - Guarantees: At-Least-Once delivery with exact per-batch offset commits     |
|    - Fault Tolerance: Local Dead-Letter Queue (data/dlq/) offline spooling      |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 3. ML Risk Scoring & Consolidation                                              |
|    - Export & Deduplication: hdfs/export_hdfs_data.py                           |
|    - Model: ml/models/attrition_model.pkl (Scikit-Learn Logistic Regression)    |
|    - Scoring: ml/predict.py                                                     |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| 4. HR Analytics Dashboard (Streamlit)                                           |
|    - Dashboard App: streamlit run dashboard/app.py (Port 8501)                  |
|    - Real-Time Risk KPIs, Department Breakdowns, Key Driver Analysis            |
+---------------------------------------------------------------------------------+
```

---

## 3. Tech Stack

- **Streaming & Messaging:** Apache Kafka 3.8.0
- **Distributed Storage:** Apache Hadoop HDFS 3.3.6 (NameNode + DataNode + WebHDFS)
- **Machine Learning:** Python, Scikit-Learn, Pandas, NumPy, Joblib
- **Visualization & Dashboard:** Streamlit, Matplotlib, Seaborn
- **Containerization:** Docker & Docker Compose

---

## 4. Getting Started

### Prerequisites
- Docker Desktop (running)
- Python 3.10+
- Git

### Step 1: Clone & Setup Virtual Environment
```powershell
git clone https://github.com/ANAGHA74/Employee-Attrition-Risk-Prediction.git
cd bdaproject

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Start Docker Services (Kafka, Kafka UI, HDFS NameNode, DataNode)
```powershell
docker compose up -d
docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --topic employee-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists
```

### Step 3: Initialize HDFS Directories
```powershell
python -c "import sys; sys.path.insert(0, 'hdfs'); from hdfs_utils import setup_hdfs_directories; setup_hdfs_directories()"
```

---

## 5. Running the Complete Pipeline

Open 3 terminals (with the virtual environment activated):

### Terminal 1: Run the Official Kafka-to-HDFS Consumer
```powershell
python hdfs/kafka_hdfs_consumer.py --batch-size 50
```
*Consumes messages from Kafka, buffers them in batches of 50, persists to `/user/hr_attrition/raw/` on HDFS, and safely commits Kafka offsets only after HDFS write confirmation.*

*(Optional: To view raw streaming messages on console without HDFS writing, run `python kafka_pipeline/consumer.py`)*

### Terminal 2: Stream Employee Records via Producer
```powershell
# Send 100 sample records
python kafka_pipeline/producer.py --delay 0.01 --limit 100

# Or stream the entire dataset of 1470 employees
python kafka_pipeline/producer.py --delay 0.01
```

### Terminal 3: Export HDFS Data & Launch the HR Dashboard
```powershell
# Export data from HDFS and run risk predictions
python hdfs/export_hdfs_data.py --predict

# Launch the Streamlit dashboard
streamlit run dashboard/app.py
```
Open `http://localhost:8501` in your web browser.

---

## 6. Verification and Automated Testing

Run the end-to-end 8-step test suite:
```powershell
python hdfs/test_hdfs.py
```
*Verifies: HDFS Health, Directory Creation, HDFS Write/Read, Kafka Ingestion, Record Persistence, Consumer Restart, ML Model Compatibility, and DLQ Spool/Replay.*

---

## 7. Web Consoles

| Tool | URL | Purpose |
| :--- | :--- | :--- |
| **HR Streamlit Dashboard** | [http://localhost:8501](http://localhost:8501) | Interactive employee risk scores & analytics |
| **HDFS NameNode UI** | [http://localhost:9870](http://localhost:9870) | Browse HDFS filesystem (`/user/hr_attrition/raw/`) |
| **Kafka UI** | [http://localhost:8080](http://localhost:8080) | Inspect topics, partitions, and streaming messages |

---

## 8. Repository Structure

```
bdaproject/
├── dashboard/
│   └── app.py                      # Streamlit HR Analytics & Risk Dashboard
├── data/
│   ├── raw/                        # Original IBM HR Dataset CSV
│   ├── processed/                  # Cleaned and HDFS-exported datasets
│   └── dlq/                        # Offline Dead-Letter Queue buffer
├── docker-compose.yml              # Multi-container Kafka + Hadoop HDFS definition
├── hdfs/                           # Person 2: HDFS Storage & Kafka Consumer Module
│   ├── README.md                   # HDFS documentation and runbook
│   ├── core-site.xml               # Hadoop core configuration
│   ├── hdfs-site.xml               # WebHDFS & replication configuration
│   ├── hdfs_utils.py               # WebHDFS REST client & DLQ utilities
│   ├── kafka_hdfs_consumer.py      # Official Kafka-to-HDFS consumer
│   ├── export_hdfs_data.py         # Batch export & ML inference bridge
│   ├── test_hdfs.py                # Automated 8-step test suite
│   └── requirements.txt            # HDFS-specific dependencies
├── kafka_pipeline/                 # Person 1: Kafka Streaming Ingestion
│   ├── config.py                   # Broker & topic settings
│   ├── producer.py                 # Employee record streaming producer
│   └── consumer.py                 # Live console stream viewer
├── ml/                             # Person 3: Machine Learning Model
│   ├── train.py                    # Trains Logistic Regression & Random Forest
│   ├── predict.py                  # Predicts attrition risk & HR review flags
│   ├── evaluate.py                 # Evaluates accuracy, recall, and ROC-AUC
│   ├── feature_importance.py       # Identifies top departure factors
│   ├── models/attrition_model.pkl  # Trained Scikit-Learn pipeline weights
│   └── results/                    # Prediction outputs & metrics
├── preprocess.py                   # Preprocesses raw IBM HR dataset
├── verify.py                       # Verifies Kafka message delivery
└── requirements.txt                # Root dependencies
```

---

## 9. About

Built as a Big Data Analytics course project at **Dayananda Sagar College of Engineering**, Department of Computer Science and Engineering.