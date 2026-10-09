"""
HDFS Utility Module for Employee Attrition Risk Prediction.
Provides robust WebHDFS REST API communication and CLI fallback for
distributed storage in Hadoop HDFS.
"""

import os
import io
import json
import time
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, urlunparse

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("HDFS_Utils")

# Configuration via Environment Variables with sensible defaults
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEBHDFS_HOST = os.getenv("WEBHDFS_HOST", "localhost")
WEBHDFS_PORT = int(os.getenv("WEBHDFS_PORT", "9870"))
DATANODE_PORT = int(os.getenv("DATANODE_PORT", "9864"))
HDFS_USER = os.getenv("HDFS_USER", "root")

BASE_WEBHDFS_URL = f"http://{WEBHDFS_HOST}:{WEBHDFS_PORT}/webhdfs/v1"
HDFS_RAW_DIR = os.getenv("HDFS_RAW_DIR", "/user/hr_attrition/raw")
HDFS_PROCESSED_DIR = os.getenv("HDFS_PROCESSED_DIR", "/user/hr_attrition/processed")
HDFS_ARCHIVE_DIR = os.getenv("HDFS_ARCHIVE_DIR", "/user/hr_attrition/archive")

LOCAL_DLQ_DIR = PROJECT_ROOT / "data" / "dlq"


def _rewrite_datanode_url(redirect_url: str) -> str:
    """
    Rewrite internal Docker hostname to localhost for host-to-container WebHDFS data transfer.
    When NameNode sends a 307 redirect, it points to internal DataNode container hostname.
    We rewrite the host to WEBHDFS_HOST (localhost) while preserving the port and query params.
    """
    parsed = urlparse(redirect_url)
    # Replace internal hostname with the accessible host
    port = parsed.port or DATANODE_PORT
    new_netloc = f"{WEBHDFS_HOST}:{port}"
    rewritten = urlunparse((
        parsed.scheme,
        new_netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    return rewritten


def check_hdfs_connection(timeout: int = 5) -> bool:
    """
    Check if Hadoop NameNode and WebHDFS are accessible.
    
    Returns:
        bool: True if NameNode responds, False otherwise.
    """
    url = f"{BASE_WEBHDFS_URL}/?op=GETFILESTATUS&user.name={HDFS_USER}"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code in (200, 403, 404):
            logger.info("Connected to Hadoop HDFS NameNode at %s:%s", WEBHDFS_HOST, WEBHDFS_PORT)
            return True
        logger.warning("HDFS returned unexpected status %s: %s", response.status_code, response.text)
        return False
    except requests.exceptions.RequestException as e:
        logger.error("Failed to connect to HDFS at %s:%s: %s", WEBHDFS_HOST, WEBHDFS_PORT, e)
        return False


def create_hdfs_directory(hdfs_path: str) -> bool:
    """
    Create a directory in HDFS if it does not already exist.
    
    Args:
        hdfs_path: Directory path in HDFS (e.g., /user/hr_attrition/raw)
        
    Returns:
        bool: True if created or exists, False on failure.
    """
    clean_path = "/" + hdfs_path.strip("/")
    url = f"{BASE_WEBHDFS_URL}{clean_path}?op=MKDIRS&user.name={HDFS_USER}&permission=755"
    try:
        response = requests.put(url, timeout=10)
        if response.status_code == 200:
            result = response.json().get("boolean", False)
            if result:
                logger.info("Successfully created/verified HDFS directory: %s", clean_path)
            return bool(result)
        logger.error("Failed to create directory %s: HTTP %s %s", clean_path, response.status_code, response.text)
        return False
    except Exception as e:
        logger.error("Error creating directory %s: %s", clean_path, e)
        return False


def setup_hdfs_directories() -> bool:
    """
    Initialize standard HDFS directory structure for the HR attrition pipeline:
    - /user/hr_attrition/raw/
    - /user/hr_attrition/processed/
    - /user/hr_attrition/archive/
    """
    dirs = [HDFS_RAW_DIR, HDFS_PROCESSED_DIR, HDFS_ARCHIVE_DIR]
    success = True
    for d in dirs:
        ok = create_hdfs_directory(d)
        if not ok:
            success = False
    return success


def write_file_to_hdfs(hdfs_file_path: str, data: bytes, overwrite: bool = True) -> bool:
    """
    Write binary/text data to an HDFS file using the WebHDFS two-step creation flow.
    Step 1: Send PUT request to NameNode (gets 307 Redirect to DataNode).
    Step 2: Send PUT request with data payload to DataNode.
    """
    clean_path = "/" + hdfs_file_path.strip("/")
    url = f"{BASE_WEBHDFS_URL}{clean_path}?op=CREATE&user.name={HDFS_USER}&overwrite={str(overwrite).lower()}"
    
    try:
        # Step 1: Request upload location from NameNode without following redirect automatically
        init_res = requests.put(url, allow_redirects=False, timeout=10)
        if init_res.status_code not in (307, 201):
            logger.error("Step 1 failed for %s: HTTP %s %s", clean_path, init_res.status_code, init_res.text)
            return False
            
        location = init_res.headers.get("Location")
        if not location:
            logger.error("No Location header returned by NameNode for %s", clean_path)
            return False
            
        # Step 2: Rewrite hostname if necessary and stream data payload to DataNode
        datanode_url = _rewrite_datanode_url(location)
        upload_res = requests.put(
            datanode_url,
            data=data,
            headers={"Content-Type": "application/octet-stream"},
            timeout=30
        )
        
        if upload_res.status_code in (200, 201):
            logger.info("Successfully wrote %d bytes to HDFS: %s", len(data), clean_path)
            return True
        else:
            logger.error("Step 2 DataNode upload failed: HTTP %s %s", upload_res.status_code, upload_res.text)
            return False
            
    except Exception as e:
        logger.error("Exception writing file to HDFS %s: %s", clean_path, e)
        return False


def write_batch_to_hdfs(
    records: List[Dict[str, Any]],
    destination_dir: str = HDFS_RAW_DIR,
    file_format: str = "jsonl",
    batch_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Write a batch of employee records to HDFS.
    Formats records as JSON Lines (.jsonl) or CSV.
    If HDFS is unavailable, safely saves the batch to local Dead-Letter Queue (DLQ).
    
    Args:
        records: List of employee record dictionaries.
        destination_dir: Target HDFS directory (default /user/hr_attrition/raw).
        file_format: 'jsonl' (default) or 'csv'.
        batch_id: Optional identifier string.
        
    Returns:
        Tuple[bool, str]: (Success status, HDFS path or local DLQ path)
    """
    if not records:
        logger.warning("Empty records batch passed to write_batch_to_hdfs")
        return True, ""
        
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    short_uid = uuid.uuid4().hex[:6]
    bid = batch_id or f"batch_{now_str}_{short_uid}"
    
    # Format the data
    if file_format.lower() == "csv":
        df = pd.DataFrame(records)
        data_bytes = df.to_csv(index=False).encode("utf-8")
        filename = f"{bid}.csv"
    else:
        # JSON Lines: each line is a self-contained JSON object
        lines = [json.dumps(r) for r in records]
        data_bytes = ("\n".join(lines) + "\n").encode("utf-8")
        filename = f"{bid}.jsonl"
        
    hdfs_file_path = f"{destination_dir.rstrip('/')}/{filename}"
    
    # Attempt write to HDFS
    success = write_file_to_hdfs(hdfs_file_path, data_bytes, overwrite=True)
    
    if success:
        return True, hdfs_file_path
    else:
        # Spool to local Dead-Letter Queue (DLQ) to ensure ZERO data loss
        LOCAL_DLQ_DIR.mkdir(parents=True, exist_ok=True)
        local_dlq_path = LOCAL_DLQ_DIR / filename
        with open(local_dlq_path, "wb") as f:
            f.write(data_bytes)
        logger.warning(
            "HDFS write failed. Safely spooled batch (%d records) to local DLQ: %s",
            len(records), local_dlq_path
        )
        return False, str(local_dlq_path)


def read_hdfs_file(hdfs_file_path: str) -> Optional[str]:
    """
    Read text content of a file from HDFS via WebHDFS.
    """
    clean_path = "/" + hdfs_file_path.strip("/")
    url = f"{BASE_WEBHDFS_URL}{clean_path}?op=OPEN&user.name={HDFS_USER}"
    
    try:
        # Step 1: Send OPEN request (NameNode returns 307 redirect to DataNode)
        res = requests.get(url, allow_redirects=False, timeout=10)
        if res.status_code == 307:
            location = res.headers.get("Location")
            datanode_url = _rewrite_datanode_url(location)
            read_res = requests.get(datanode_url, timeout=30)
            if read_res.status_code == 200:
                return read_res.text
            else:
                logger.error("Failed to read from DataNode: HTTP %s", read_res.status_code)
                return None
        elif res.status_code == 200:
            return res.text
        else:
            logger.error("Failed to open file %s: HTTP %s %s", clean_path, res.status_code, res.text)
            return None
    except Exception as e:
        logger.error("Exception reading HDFS file %s: %s", clean_path, e)
        return None


def list_hdfs_directory(hdfs_path: str) -> List[Dict[str, Any]]:
    """
    List files and directories within an HDFS path.
    
    Returns:
        List of file status dictionaries containing 'pathSuffix', 'type', 'length', etc.
    """
    clean_path = "/" + hdfs_path.strip("/")
    url = f"{BASE_WEBHDFS_URL}{clean_path}?op=LISTSTATUS&user.name={HDFS_USER}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            statuses = response.json().get("FileStatuses", {}).get("FileStatus", [])
            return statuses
        logger.warning("Could not list directory %s: HTTP %s", clean_path, response.status_code)
        return []
    except Exception as e:
        logger.error("Exception listing directory %s: %s", clean_path, e)
        return []


def read_all_records_from_hdfs(directory_path: str = HDFS_RAW_DIR) -> List[Dict[str, Any]]:
    """
    Read all batch files in an HDFS directory and return a combined list of employee records.
    Supports both .jsonl and .csv batch files.
    """
    files = list_hdfs_directory(directory_path)
    all_records = []
    
    clean_dir = "/" + directory_path.strip("/")
    for f in sorted(files, key=lambda x: x.get("pathSuffix", "")):
        if f.get("type") != "FILE":
            continue
        suffix = f.get("pathSuffix", "")
        file_path = f"{clean_dir}/{suffix}"
        
        content = read_hdfs_file(file_path)
        if not content:
            continue
            
        if suffix.endswith(".jsonl"):
            for line in content.strip().splitlines():
                if line.strip():
                    try:
                        record = json.loads(line)
                        all_records.append(record)
                    except json.JSONDecodeError as err:
                        logger.warning("Malformed JSON in %s: %s", file_path, err)
        elif suffix.endswith(".csv"):
            df = pd.read_csv(io.StringIO(content))
            records = df.to_dict(orient="records")
            all_records.extend(records)
            
    return all_records


def replay_dlq_to_hdfs() -> Dict[str, Any]:
    """
    Replay any batches previously saved in the local Dead-Letter Queue (DLQ) back into HDFS.
    
    Returns:
        Dict[str, Any]: Detailed statistics on replayed batches and records.
    """
    if not LOCAL_DLQ_DIR.exists():
        return {"replayed_batches": 0, "replayed_records": 0, "failed_batches": 0}
        
    dlq_files = list(LOCAL_DLQ_DIR.glob("*.jsonl")) + list(LOCAL_DLQ_DIR.glob("*.csv"))
    if not dlq_files:
        return {"replayed_batches": 0, "replayed_records": 0, "failed_batches": 0}
        
    logger.info("Found %d pending DLQ batch(es) to replay to HDFS", len(dlq_files))
    replayed_batches = 0
    replayed_records = 0
    failed_batches = 0
    
    for file_path in dlq_files:
        with open(file_path, "rb") as f:
            data = f.read()
            
        # Count records in file
        if file_path.suffix == ".jsonl":
            rec_count = len([l for l in data.decode("utf-8", errors="ignore").splitlines() if l.strip()])
        else:
            rec_count = max(0, len(data.decode("utf-8", errors="ignore").splitlines()) - 1)
            
        hdfs_path = f"{HDFS_RAW_DIR.rstrip('/')}/{file_path.name}"
        success = write_file_to_hdfs(hdfs_path, data, overwrite=True)
        if success:
            logger.info("Replayed DLQ batch (%d records) to HDFS: %s", rec_count, hdfs_path)
            file_path.unlink()  # Remove local copy once safely persisted
            replayed_batches += 1
            replayed_records += rec_count
        else:
            logger.warning("Failed to replay %s to HDFS, retaining locally in DLQ.", file_path.name)
            failed_batches += 1
            
    return {
        "replayed_batches": replayed_batches,
        "replayed_records": replayed_records,
        "failed_batches": failed_batches
    }
