import boto3
import os
import time

def seed_chaos():
    endpoint = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    params = {
        "endpoint_url": endpoint,
        "aws_access_key_id": 'test',
        "aws_secret_access_key": 'test',
        "region_name": 'us-east-1'
    }
    
    ec2 = boto3.client('ec2', **params)
    s3 = boto3.client('s3', **params)
    iam = boto3.client('iam', **params)
    rds = boto3.client('rds', **params)
    cw = boto3.client('cloudwatch', **params)

    print("🔥 KRATOS: Injecting Chaos Scenarios...")

    # 1. The Scaling Anomaly: 12 instances (Trigger: >10 count rule)
    print("🚀 Scenario 1: Mass Scale-up (12x t3.medium)...")
    ec2.run_instances(ImageId='ami-12345678', InstanceType='t3.medium', MinCount=12, MaxCount=12)

    # 2. Public Data Exposure (Trigger: Policy Engine + Cost Risk)
    print("📂 Scenario 2: Publicly Accessible RDS (No Encryption)...")
    try:
        rds.create_db_instance(
            DBInstanceIdentifier='leaked-customer-data',
            Engine='postgres',
            DBInstanceClass='db.m5.large',
            PubliclyAccessible=True,
            StorageEncrypted=False,
            AllocatedStorage=20
        )
    except: pass

    # 3. The Shadow Admin (Trigger: IAM Grave-yard hour rule)
    print("🔑 Scenario 3: Creating Shadow Admin User...")
    try:
        iam.create_user(UserName='backdoor-admin')
        iam.attach_user_policy(UserName='backdoor-admin', PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')
    except: pass

    # 4. The Crypto-Miner Simulation (Trigger: T2 Statistical Spike)
    print("⛏️  Scenario 4: Simulating GPU Utilization Spike (98%)...")
    try:
        gpu = ec2.run_instances(ImageId='ami-gpu', InstanceType='g5.xlarge', MinCount=1, MaxCount=1)
        gpu_id = gpu['Instances'][0]['InstanceId']
        
        from datetime import datetime
        cw.put_metric_data(
            Namespace='AWS/EC2',
            MetricData=[{
                'MetricName': 'CPUUtilization',
                'Dimensions': [{'Name': 'InstanceId', 'Value': gpu_id}],
                'Value': 98.5,
                'Unit': 'Percent',
                'Timestamp': datetime.utcnow()
            }]
        )
    except Exception as e:
        print(f"⚠️  CloudWatch simulation skipped: {e}")

    print("\n✅ Chaos Injection Complete. Run: uv run python kratos.py")

if __name__ == "__main__":
    seed_chaos()
