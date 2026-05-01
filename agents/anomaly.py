from anomaly.engine import AnomalyEngine
from anomaly.scorer import RiskScorer

def anomaly_detection_node(state: dict):
    print("🛡️  KRATOS [Anomaly Engine]: Analyzing behavioral signals...")
    
    engine = AnomalyEngine()
    scorer = RiskScorer()
    
    anomaly_findings = []
    max_risk = 0.0
    
    # Check for EC2 anomalies in the current environment
    # In a real event-flow, this info comes from the scanner or ingestion
    import boto3
    import os
    ec2 = boto3.client('ec2', endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"), aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')
    
    try:
        instances = ec2.describe_instances()
        for res in instances.get('Reservations', []):
            for inst in res.get('Instances', []):
                event = {
                    "resource_type": "ec2",
                    "resource_id": inst['InstanceId'],
                    "instance_type": inst['InstanceType'],
                    "account_id": "local",
                    "value": 1.0 # Current presence
                }
                analysis = engine.analyze(event)
                if analysis["findings"]:
                    anomaly_findings.extend(analysis["findings"])
                
                # Calculate composite using the engine's detected risks
                comp = scorer.calculate_composite_score(
                    analysis["scores"]["policy_risk"], 
                    analysis["scores"]["anomaly_risk"], 
                    analysis["scores"]["cost_risk"]
                )
                max_risk = max(max_risk, comp)
    except Exception as e:
        print(f"Anomaly analysis error: {e}")

    return {
        "anomaly_findings": anomaly_findings,
        "composite_risk_score": max_risk,
        "status": "Anomaly Detection Complete"
    }
