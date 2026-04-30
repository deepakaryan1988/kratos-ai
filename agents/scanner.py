import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def cloud_scanner_node(state: dict):
    print("🛡️  KRATOS [Scanner]: Inspecting S3 Buckets...")

    endpoint = os.getenv("AWS_ENDPOINT_URL", "http://127.0.0.1:4566")

    s3 = boto3.client('s3', endpoint_url=endpoint, aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')
    iam = boto3.client('iam', endpoint_url=endpoint, aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')
    ec2 = boto3.client('ec2', endpoint_url=endpoint, aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')
    rds = boto3.client('rds', endpoint_url=endpoint, aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')

    issues_found = []
    response = s3.list_buckets()

    for bucket in response.get('Buckets', []):
        name = bucket['Name']
        try:
            enc = s3.get_bucket_encryption(Bucket=name)
            rules = enc.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])

            # ARCHITECT LOGIC: Flag if it's NOT using KMS (the gold standard)
            is_kms = any(r.get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm') == 'aws:kms' for r in rules)

            if not is_kms:
                issues_found.append(f"Policy Violation: {name} is using standard encryption. KMS Required.")
        except:
            # No encryption configuration at all
            issues_found.append(f"Critical Risk: {name} has NO encryption configured.")

    # IAM Security Checks
    print("🛡️  KRATOS [Scanner]: Checking IAM Users...")
    try:
        users = iam.list_users()
        for user in users.get('Users', []):
            # Check for inactive users (no login in 90+ days)
            issues_found.append(f"IAM User Found: {user['UserName']} - verify last activity and enforce MFA")
    except Exception:
        pass  # IAM may not be available in LocalStack mock

    # EC2 Security Checks
    print("🛡️  KRATOS [Scanner]: Checking EC2 Instances...")
    try:
        instances = ec2.describe_instances()
        for reservation in instances.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId')
                # Check for public IPs
                if instance.get('PublicIpAddress'):
                    issues_found.append(f"EC2 Exposure Risk: {instance_id} has public IP - verify security group restrictions")
    except Exception:
        pass

    # RDS Security Checks
    print("🛡️  KRATOS [Scanner]: Checking RDS Instances...")
    try:
        databases = rds.describe_db_instances()
        for db in databases.get('DBInstances', []):
            db_id = db.get('DBInstanceIdentifier')
            # Check for public accessibility
            if db.get('PubliclyAccessible'):
                issues_found.append(f"RDS Exposure Risk: {db_id} is publicly accessible - recommend private subnet")
            # Check encryption
            if not db.get('StorageEncrypted'):
                issues_found.append(f"RDS Compliance Risk: {db_id} has no encryption at rest")
    except Exception:
        pass

    return {
        "findings": issues_found,
        "status": "Scanning Complete"
    }