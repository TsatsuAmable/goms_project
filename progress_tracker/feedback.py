
import datetime
import statistics
from typing import Dict, List, Tuple, Any
from progress_tracker.metrics import MetricsManager, Metric

class FeedbackMechanism:
    """
    Provides automated insight generation for feeding back into the planning process.
    Based on Section 4.1 of the design document.
    """
    def __init__(self, metrics_manager: MetricsManager):
        self.metrics_manager = metrics_manager

    def _get_numeric_values(self, metric: Metric, start_time: datetime.datetime, end_time: datetime.datetime) -> List[float]:
        """Helper to extract numeric values from a metric within a period."""
        values_with_ts = metric.get_values_in_period(start_time, end_time)
        return [v for ts, v in values_with_ts if isinstance(v, (int, float))]

    def detect_anomalies(self, metric_name: str, period_days: int = 7, threshold_std_dev: float = 2.0) -> List[Dict[str, Any]]:
        """
        Simulates anomaly detection for a given metric.
        Identifies values that deviate significantly from the mean within the period.
        """
        metric = self.metrics_manager.get_metric(metric_name)
        if not metric:
            return [{"type": "Error", "message": f"Metric '{metric_name}' not found."}]

        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=period_days)
        numeric_values = self._get_numeric_values(metric, start_time, end_time)
        values_with_ts = metric.get_values_in_period(start_time, end_time)

        if len(numeric_values) < 2:
            return [{"type": "Info", "message": f"Not enough data to detect anomalies for '{metric_name}' in the last {period_days} days."}]

        mean_val = statistics.mean(numeric_values)
        std_dev = statistics.stdev(numeric_values)

        anomalies = []
        for (timestamp, value) in values_with_ts:
            if isinstance(value, (int, float)) and abs(value - mean_val) > threshold_std_dev * std_dev:
                anomalies.append({
                    "metric": metric_name,
                    "timestamp": timestamp.isoformat(),
                    "value": value,
                    "mean": round(mean_val, 2),
                    "std_dev": round(std_dev, 2),
                    "deviation": round(abs(value - mean_val), 2),
                    "insight": f"Anomaly detected: '{metric_name}' value {value}{metric.unit if metric.unit else ''} at {timestamp.strftime('%Y-%m-%d %H:%M')} significantly deviates from the mean {mean_val}{metric.unit}."
                })
        return anomalies

    def analyze_trends(self, metric_name: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Simulates trend analysis for a given metric.
        Determines if the metric is generally increasing, decreasing, or stable.
        (A simplified linear regression or simple average comparison could be used for real trends).
        """
        metric = self.metrics_manager.get_metric(metric_name)
        if not metric:
            return {"type": "Error", "message": f"Metric '{metric_name}' not found."}

        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=period_days)
        numeric_values = self._get_numeric_values(metric, start_time, end_time)

        if len(numeric_values) < 2:
            return {"type": "Info", "message": f"Not enough data to analyze trend for '{metric_name}' in the last {period_days} days."}

        # Simple trend analysis: compare average of first half vs second half
        mid_point = len(numeric_values) // 2
        if mid_point == 0: # Handle cases with only one value after filtering
            return {"type": "Info", "message": f"Not enough data to analyze trend for '{metric_name}' in the last {period_days} days."}

        first_half_avg = statistics.mean(numeric_values[:mid_point])
        second_half_avg = statistics.mean(numeric_values[mid_point:])

        trend = "stable"
        if second_half_avg > first_half_avg * 1.05: # 5% increase
            trend = "increasing"
        elif second_half_avg < first_half_avg * 0.95: # 5% decrease
            trend = "decreasing"

        insight = f"Trend for '{metric_name}' over the last {period_days} days: {trend}. "
        if trend == "increasing":
            insight += f"Average increased from {round(first_half_avg, 2)} to {round(second_half_avg, 2)}{metric.unit}."
        elif trend == "decreasing":
            insight += f"Average decreased from {round(first_half_avg, 2)} to {round(second_half_avg, 2)}{metric.unit}."
        else:
            insight += f"Average remained around {round(second_half_avg, 2)}{metric.unit}."

        return {
            "metric": metric_name,
            "period_days": period_days,
            "trend": trend,
            "first_half_avg": round(first_half_avg, 2),
            "second_half_avg": round(second_half_avg, 2),
            "insight": insight
        }

    def predictive_analytics(self, metric_name: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Simulates predictive analytics for a given metric.
        For simplicity, this will project the current trend forward.
        A real implementation would use time-series forecasting models.
        """
        metric = self.metrics_manager.get_metric(metric_name)
        if not metric:
            return {"type": "Error", "message": f"Metric '{metric_name}' not found."}

        trend_analysis = self.analyze_trends(metric_name, period_days)
        if "trend" not in trend_analysis:
            return {"type": "Info", "message": f"Cannot perform predictive analytics without trend data for '{metric_name}'."}

        last_value = metric.get_latest_value()
        if not isinstance(last_value, (int, float)):
            return {"type": "Info", "message": f"Last recorded value for '{metric_name}' is not numeric, cannot predict."}

        projected_change_rate = 0.0 # Placeholder
        if trend_analysis["trend"] == "increasing":
            projected_change_rate = 0.02 # Assume 2% increase per 'next period' (e.g., next week)
        elif trend_analysis["trend"] == "decreasing":
            projected_change_rate = -0.02 # Assume 2% decrease

        predicted_value_next_period = round(last_value * (1 + projected_change_rate), 2)
        insight = f"Predictive insight for '{metric_name}': Based on recent trends, the value is projected to be around {predicted_value_next_period}{metric.unit} in the near future (e.g., next week)."
        if projected_change_rate != 0:
            insight += f" (Current trend: {trend_analysis['trend']})."

        return {
            "metric": metric_name,
            "current_value": last_value,
            "projected_change_rate": projected_change_rate,
            "predicted_value_next_period": predicted_value_next_period,
            "insight": insight
        }

    def generate_feedback_report(self) -> str:
        """
        Generates a summary of automated insights across key metrics.
        This would be fed into architectural review and adaptation cycles.
        """
        feedback_lines = [
            f"Automated Feedback Insights - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "--------------------------------------------------",
            "\nThis report summarizes automated insights derived from metric analysis.",
            "These insights are crucial for guiding architectural review and adaptation cycles.",
            "\n1. Anomaly Detections (Last 7 Days):"
        ]

        # Example metrics to run anomaly detection on
        metrics_for_anomaly = ["Compute Unit Consumption", "Critical System Failure Rate", "Latency & Response Times"]
        all_anomalies = []
        for metric_name in metrics_for_anomaly:
            anomalies = self.detect_anomalies(metric_name, period_days=7)
            all_anomalies.extend(anomalies)

        if all_anomalies:
            for anomaly in all_anomalies:
                feedback_lines.append(f"   - {anomaly['insight']}")
        else:
            feedback_lines.append("   - No significant anomalies detected in key metrics.")

        feedback_lines.append("\n2. Trend Analysis (Last 30 Days):")
        # Example metrics to run trend analysis on
        metrics_for_trend = ["Task Success Rate", "Knowledge Base Expansion Rate", "Energy Consumption"]
        for metric_name in metrics_for_trend:
            trend = self.analyze_trends(metric_name, period_days=30)
            if "insight" in trend:
                feedback_lines.append(f"   - {trend['insight']}")
            else:
                feedback_lines.append(f"   - Could not analyze trend for '{metric_name}': {trend.get('message', 'N/A')}")

        feedback_lines.append("\n3. Predictive Insights:")
        # Example metrics for predictive analytics
        metrics_for_predictive = ["Storage Utilization", "Objective Attainment Score", "Anomaly Resolution Rate"]
        for metric_name in metrics_for_predictive:
            prediction = self.predictive_analytics(metric_name, period_days=30)
            if "insight" in prediction:
                feedback_lines.append(f"   - {prediction['insight']}")
            else:
                feedback_lines.append(f"   - Could not generate prediction for '{metric_name}': {prediction.get('message', 'N/A')}")

        feedback_lines.append("\n--- Actionable Recommendations (Simulated) ---")
        feedback_lines.append("Based on the above insights, consider the following for planning:")
        feedback_lines.append("   - Investigate the root cause of the detected 'Compute Unit Consumption' anomaly if it persists.")
        feedback_lines.append("   - Prioritize architectural adjustments to further improve 'Task Success Rate' given its positive trend.")
        feedback_lines.append("   - Monitor 'Storage Utilization' closely, as predictive models suggest continued growth, potentially requiring capacity planning.")
        feedback_lines.append("--------------------------------------------------")

        return "\n".join(feedback_lines)

if __name__ == "__main__":
    # Initialize metrics and simulate data
    metrics_manager = MetricsManager()
    # Add a few metrics for immediate testing
    metrics_manager.add_metric(Metric("Test Anomaly Metric", "Test", "Metric for anomaly detection.", unit="units"))
    metrics_manager.add_metric(Metric("Test Trend Metric", "Test", "Metric for trend analysis.", unit="val"))
    metrics_manager.add_metric(Metric("Test Predictive Metric", "Test", "Metric for predictive analysis.", unit="score"))

    # Simulate data, including some potential anomalies for demonstration
    now = datetime.datetime.now()
    for i in range(35): # Simulate 35 days of data
        timestamp = now - datetime.timedelta(days=35 - i)
        val_anomaly = random.uniform(100, 150)
        if i == 30 or i == 31: # Inject a couple of anomalies
            val_anomaly = random.uniform(250, 300)
        metrics_manager.record_metric_value("Test Anomaly Metric", val_anomaly, timestamp)
        metrics_manager.record_metric_value("Test Trend Metric", 100 + i * 0.5 + random.uniform(-5, 5), timestamp) # Increasing trend
        metrics_manager.record_metric_value("Test Predictive Metric", 80 - i * 0.2 + random.uniform(-3, 3), timestamp) # Decreasing trend

    # Use the full initialized metrics for more comprehensive feedback
    full_metrics_manager = metrics_manager # Could also use initialize_metrics()
    # full_metrics_manager.simulate_data(num_days=40) # Simulate more data if needed for broader analysis

    feedback_mechanism = FeedbackMechanism(full_metrics_manager)

    print("\n--- Generating Automated Feedback Insights Report ---")
    feedback_report = feedback_mechanism.generate_feedback_report()
    print(feedback_report)

    print("\n--- Testing Individual Anomaly Detection ---")
    anomalies = feedback_mechanism.detect_anomalies("Test Anomaly Metric", period_days=7)
    if anomalies:
        for anomaly in anomalies:
            print(f"Anomaly: {anomaly['insight']}")
    else:
        print("No anomalies detected for 'Test Anomaly Metric'.")

    print("\n--- Testing Individual Trend Analysis ---")
    trend = feedback_mechanism.analyze_trends("Test Trend Metric", period_days=15)
    print(f"Trend for 'Test Trend Metric': {trend.get('insight', 'N/A')}")

    print("\n--- Testing Individual Predictive Analytics ---")
    prediction = feedback_mechanism.predictive_analytics("Test Predictive Metric", period_days=15)
    print(f"Prediction for 'Test Predictive Metric': {prediction.get('insight', 'N/A')}")
