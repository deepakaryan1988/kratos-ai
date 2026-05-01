import boto3
import os
from datetime import datetime, timedelta
from typing import List, Dict
from anomaly.engine import AnomalyEngine
from anomaly.scorer import RiskScorer

class MetricCollector:
    """Collects metrics from CloudWatch and feeds them to the Anomaly Engine."""
    
    def __init__(self):
        self.engine = AnomalyEngine()
        self.scorer = RiskScorer()
        self.cw = boto3.client(
            'cloudwatch',
            endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1'
        )

    def collect_ec2_metrics(self) -> List[Dict]:
        """Collect CPU utilization for all EC2 instances."""
        # In a real system, we'd list instances first. 
        # For MVP/LocalStack, we assume some known IDs or fetch them.
        ec2 = boto3.client(
            'ec2',
            endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1'
        )
        
        findings = []
        try:
            instances = ec2.describe_instances()
            for reservation in instances.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    
                    # Fetch CPU metric
                    stats = self.cw.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=datetime.utcnow() - timedelta(minutes=10),
                        EndTime=datetime.utcnow(),
                        Period=300,
                        Statistics=['Average']
                    )
                    
                    if stats['Datapoints']:
                        avg_cpu = stats['Datapoints'][0]['Average']
                        
                        # Feed to Anomaly Engine
                        event = {
                            "account_id": "local",
                            "region": "us-east-1",
                            "resource_type": "ec2",
                            "resource_id": instance_id,
                            "instance_type": instance_type,
                            "metric_name": "CPUUtilization",
                            "value": avg_cpu,
                            "instance_count": 1
                        }
                        
                        analysis = self.engine.analyze(event)
                        
                        # Calculate composite score
                        composite = self.scorer.calculate_composite_score(
                            analysis["scores"]["policy_risk"],
                            analysis["scores"]["anomaly_risk"],
                            analysis["scores"]["cost_risk"]
                        )
                        
                        if composite > 30:
                            findings.append({
                                "resource": instance_id,
                                "composite_score": composite,
                                "analysis": analysis
                            })
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            
        return findings

if __name__ == "__main__":
    collector = MetricCollector()
    print("🚀 Running Batch Metric Collection...")
    results = collector.collect_ec2_metrics()
    for r in results:
        print(f"⚠️ Anomaly Detected: {r['resource']} | Score: {r['composite_score']:.2f}")
