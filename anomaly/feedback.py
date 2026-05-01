from vault.policy_store import get_connection

class AnomalyFeedback:
    """Handles feedback from the approval system to tune detection thresholds."""
    
    @staticmethod
    def record_feedback(anomaly_id: int, feedback_type: str):
        """
        Record user feedback (true_positive/false_positive) and update the event status.
        """
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Update anomaly event status
            status = 'alerted' if feedback_type == 'true_positive' else 'ignored'
            cur.execute(
                "UPDATE anomaly_events SET feedback = %s, status = %s WHERE id = %s",
                (feedback_type, status, anomaly_id)
            )
            
            # Store detail in feedback table
            cur.execute(
                "INSERT INTO anomaly_feedback (anomaly_id, feedback, source) VALUES (%s, %s, %s)",
                (anomaly_id, feedback_type, 'approval_gate')
            )
            conn.commit()
            print(f"✅ Feedback recorded for Anomaly #{anomaly_id}: {feedback_type}")
        except Exception as e:
            print(f"Error recording feedback: {e}")
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_stats():
        """Retrieve system performance stats."""
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*), feedback FROM anomaly_events GROUP BY feedback")
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
