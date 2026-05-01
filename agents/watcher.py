import time
import hashlib
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class ChangeWatcher:
    def __init__(self, interval=60):
        self.interval = interval
        self.last_state = None
        # Use centralized AWS endpoint config
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1'
        )

    def get_state_hash(self):
        """Get hash of current bucket state"""
        try:
            response = self.s3.list_buckets()
            buckets = sorted([b['Name'] + str(b['CreationDate']) for b in response.get('Buckets', [])])
            return hashlib.md5(str(buckets).encode()).hexdigest()
        except:
            return None

    def detect_change(self):
        """Check if infrastructure changed"""
        current = self.get_state_hash()
        if current and current != self.last_state:
            self.last_state = current
            return True
        if current:
            self.last_state = current
        return False

    def start(self, callback):
        """Start watching for changes"""
        print(f"🤖 KRATOS Agent: Watching for changes (interval: {self.interval}s)")
        while True:
            if self.detect_change():
                print("🔔 Change detected! Scanning...")
                callback()
            time.sleep(self.interval)
