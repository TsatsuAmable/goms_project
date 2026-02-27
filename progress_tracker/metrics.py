
import datetime
import random
from typing import Dict, Any

class Metric:
    """
    Represents a single metric for progress tracking.
    """
    def __init__(self, name: str, category: str, description: str, unit: str = None):
        self.name = name
        self.category = category
        self.description = description
        self.unit = unit
        self.values = [] # Stores (timestamp, value) tuples

    def record_value(self, value: Any, timestamp: datetime.datetime = None):
        """Records a new value for the metric."""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        self.values.append((timestamp, value))

    def get_latest_value(self):
        """Returns the latest recorded value."""
        if not self.values:
            return None
        return self.values[-1][1]

    def get_values_in_period(self, start_time: datetime.datetime, end_time: datetime.datetime):
        """Returns values recorded within a specific time period."""
        return [(ts, val) for ts, val in self.values if start_time <= ts <= end_time]

    def __repr__(self):
        return f"Metric(name='{self.name}', category='{self.category}', latest_value={self.get_latest_value()})"

class MetricsManager:
    """
    Manages a collection of metrics.
    """
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}

    def add_metric(self, metric: Metric):
        """Adds a metric to the manager."""
        if metric.name in self.metrics:
            print(f"Warning: Metric '{metric.name}' already exists and will be overwritten.")
        self.metrics[metric.name] = metric

    def get_metric(self, name: str) -> Metric:
        """Retrieves a metric by its name."""
        return self.metrics.get(name)

    def get_metrics_by_category(self, category: str) -> Dict[str, Metric]:
        """Returns a dictionary of metrics belonging to a specific category."""
        return {name: metric for name, metric in self.metrics.items() if metric.category == category}

    def record_metric_value(self, metric_name: str, value: Any, timestamp: datetime.datetime = None):
        """Records a value for a specific metric."""
        metric = self.get_metric(metric_name)
        if metric:
            metric.record_value(value, timestamp)
        else:
            print(f"Error: Metric '{metric_name}' not found.")

    def simulate_data(self, num_days: int = 7):
        """
        Simulates data for all registered metrics for a given number of days.
        This is for demonstration purposes.
        """
        now = datetime.datetime.now()
        for metric_name, metric in self.metrics.items():
            print(f"Simulating data for {metric_name}...")
            for i in range(num_days * 24): # Hourly data for num_days
                timestamp = now - datetime.timedelta(hours=num_days*24 - i)
                if "Rate" in metric.name or "Percentage" in metric.name:
                    value = random.uniform(0.7, 0.99) # e.g., success rate, uptime percentage
                elif "Time" in metric.name:
                    value = random.uniform(5, 600) # e.g., completion time in seconds
                elif "Score" in metric.name:
                    value = random.uniform(0, 100) # e.g., attainment score
                elif "Consumption" in metric.name or "Utilization" in metric.name or "Usage" in metric.name:
                    value = random.uniform(100, 10000) # e.g., compute units, storage
                elif "Frequency" in metric.name or "Count" in metric.name or "Instances" in metric.name:
                    value = random.randint(0, 10) # e.g., update frequency, incident count
                elif "Growth" in metric.name:
                    value = random.uniform(0.01, 0.1) # e.g., knowledge base expansion rate
                else:
                    value = random.uniform(0, 100) # Generic value
                metric.record_value(round(value, 2), timestamp)

# --- Metric Definitions ---
# These are examples based on the design document (Section 2)

def initialize_metrics() -> MetricsManager:
    """Initializes and returns a MetricsManager with predefined metrics."""
    manager = MetricsManager()

    # 2.1 Task Completion & Mission Objectives
    manager.add_metric(Metric("Task Success Rate", "Task Completion", "Percentage of successfully completed tasks out of planned tasks.", unit="%"))
    manager.add_metric(Metric("Task Completion Time", "Task Completion", "Average time taken to complete specific types of tasks.", unit="seconds"))
    manager.add_metric(Metric("Milestone Achievement", "Task Completion", "Tracking progress against predefined mission milestones.", unit="count"))
    manager.add_metric(Metric("Objective Attainment Score", "Task Completion", "A weighted score reflecting the progress towards high-level mission objectives.", unit="score"))

    # 2.2 System Autonomy & Adaptability
    manager.add_metric(Metric("Autonomous Decision Rate", "System Autonomy", "Percentage of decisions made without human intervention.", unit="%"))
    manager.add_metric(Metric("Adaptation Cycle Time", "System Autonomy", "Time taken from identifying a need for architectural change to its successful implementation.", unit="hours"))
    manager.add_metric(Metric("Resource Reallocation Efficiency", "System Autonomy", "How effectively resources are shifted based on changing mission needs or internal state.", unit="ratio"))
    manager.add_metric(Metric("Anomaly Resolution Rate", "System Autonomy", "Percentage of system anomalies detected and resolved autonomously.", unit="%"))

    # 2.3 Resource Utilization & Efficiency
    manager.add_metric(Metric("Compute Unit Consumption", "Resource Utilization", "Tracking processing power usage over time.", unit="units"))
    manager.add_metric(Metric("Energy Consumption", "Resource Utilization", "Monitoring energy usage for various operations.", unit="kWh"))
    manager.add_metric(Metric("Storage Utilization", "Resource Utilization", "Percentage of used storage capacity.", unit="%"))
    manager.add_metric(Metric("Communication Bandwidth Usage", "Resource Utilization", "Data transfer rates and network load.", unit="Mbps"))

    # 2.4 Learning & Improvement
    manager.add_metric(Metric("Model Update Frequency", "Learning & Improvement", "How often AI/ML models are retrained or updated.", unit="times/week"))
    manager.add_metric(Metric("Knowledge Base Expansion Rate", "Learning & Improvement", "Growth of the system's internal knowledge and learned patterns.", unit="ratio/day"))
    manager.add_metric(Metric("Error Reduction Rate", "Learning & Improvement", "Decrease in specific types of operational errors or failures over time.", unit="%"))
    manager.add_metric(Metric("Novel Problem Solving Instances", "Learning & Improvement", "Number of unique problems solved without prior programming or human guidance.", unit="count"))

    # 2.5 System Health & Stability
    manager.add_metric(Metric("Uptime Percentage", "System Health", "Overall system availability.", unit="%"))
    manager.add_metric(Metric("Critical System Failure Rate", "System Health", "Frequency of failures in core architectural components.", unit="count/day"))
    manager.add_metric(Metric("Latency & Response Times", "System Health", "Performance metrics for critical operations.", unit="ms"))
    manager.add_metric(Metric("Security Incident Count", "System Health", "Number of detected and mitigated security events.", unit="count/day"))

    return manager

if __name__ == "__main__":
    metrics_manager = initialize_metrics()
    print("Metrics initialized:")
    for metric_name, metric in metrics_manager.metrics.items():
        print(f"- {metric.name} ({metric.category})")

    print("\nSimulating data for 3 days...")
    metrics_manager.simulate_data(num_days=3)

    print("\nLatest values after simulation:")
    for metric_name, metric in metrics_manager.metrics.items():
        print(f"- {metric.name}: {metric.get_latest_value()} {metric.unit if metric.unit else ''}")

    # Example of getting values for a specific period
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    task_success_rate = metrics_manager.get_metric("Task Success Rate")
    if task_success_rate:
        values_yesterday = task_success_rate.get_values_in_period(yesterday, now)
        print(f"\nTask Success Rate values in last 24 hours: {len(values_yesterday)} entries.")
        # for ts, val in values_yesterday:
        #     print(f"  {ts}: {val}")
