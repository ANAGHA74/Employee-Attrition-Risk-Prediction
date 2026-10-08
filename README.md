# Employee Attrition Risk Prediction

A Big Data pipeline that estimates how likely each employee is to leave a company, so HR can step in **before** someone resigns.

## The problem

HR teams usually find out an employee is leaving only when the resignation letter arrives, which is too late to do anything about it. This project scores every employee's attrition risk early. Anyone with a score of **0.6 or higher** is flagged for HR review.

## How it works

```
Employee data (CSV) -> Kafka -> HDFS -> ML model -> HR dashboard
```

1. **Kafka** streams employee records one by one, like a live feed.
2. **HDFS** (Hadoop) stores the incoming data.
3. A **classification model** gives each employee a risk score between 0 and 1.
4. An **HR dashboard** shows who is at risk, and why.

**Dataset:** [IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) (1470 employees, fictional data).

**Note:** the dataset records whether an employee eventually left, not exactly when, so the score is an attrition-likelihood estimate interpreted as near-term risk, not an exact 6-month prediction.

## Tech stack

Python, Apache Kafka, Hadoop HDFS, scikit-learn, Streamlit, Docker

## Project status

| Component | Status |
|---|---|
| Kafka data ingestion (`kafka_pipeline/`) | Done and verified (1470 of 1470 messages) |
| HDFS storage | In progress |
| ML risk model | In progress |
| HR dashboard | In progress |

## Try the Kafka part

**You need:** Docker Desktop (running), Python 3.11+, Git.

```powershell
git clone https://github.com/ANAGHA74/Employee-Attrition-Risk-Prediction.git
cd Employee-Attrition-Risk-Prediction

docker compose up -d
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --create --topic employee-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Open two terminals (with the venv activated in both):

```powershell
# Terminal 1: receives the data
python kafka_pipeline\consumer.py

# Terminal 2: sends the data (use --limit 100 for a quick test)
python kafka_pipeline\producer.py --delay 0.02
```

Then check the result:
- `python verify.py` prints **PASS** if all 1470 employees reached Kafka.
- Or open http://localhost:8080 (Kafka UI) -> Topics -> `employee-data`.

If the consumer shows nothing on a second run, start it with a new group name: `$env:GROUP_ID="new-name"`.

## Folder structure

```
data/               Raw and cleaned datasets
kafka_pipeline/     Producer, consumer and config
docker-compose.yml  Starts Kafka and Kafka UI
preprocess.py       Cleans the raw dataset
verify.py           Checks that all messages arrived
```

## About

Built as a Big Data Analytics course project at Dayananda Sagar College of Engineering, Department of Computer Science and Engineering.