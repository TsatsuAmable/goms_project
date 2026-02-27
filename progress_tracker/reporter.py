
import datetime
from typing import List, Dict, Any
from progress_tracker.metrics import MetricsManager, Metric

class Reporter:
    """
    Generates various status reports based on collected metrics.
    """
    def __init__(self, metrics_manager: MetricsManager):
        self.metrics_manager = metrics_manager

    def _get_metric_summary(self, metric: Metric, start_time: datetime.datetime, end_time: datetime.datetime) -> Dict[str, Any]:
        """Helper to get a summary (latest, average) for a single metric."""
        values = metric.get_values_in_period(start_time, end_time)
        if not values:
            return {"latest": "N/A", "average": "N/A", "unit": metric.unit if metric.unit else ""}

        numeric_values = [v for ts, v in values if isinstance(v, (int, float))]
        latest_value = values[-1][1] if values else "N/A"
        average_value = round(sum(numeric_values) / len(numeric_values), 2) if numeric_values else "N/A"

        return {
            "latest": latest_value,
            "average": average_value,
            "unit": metric.unit if metric.unit else ""
        }

    def generate_daily_report(self) -> str:
        """
        Generates a concise daily status report.
        Content based on Section 3.1 of the design document.
        """
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=24)

        report_lines = [
            f"Daily Status Report - {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "--------------------------------------------------",
            "\n1. Key Activities & Status (Last 24 Hours):",
            "   - Core tasks completed: [Simulated: X tasks completed]",
            "   - Critical issues/anomalies: [Simulated: None/Few]",
            "   - High-priority tasks status: [Simulated: On track/Minor delays]",
            "\n2. Key Metric Snapshots:",
        ]

        # Select a few key metrics for a quick snapshot
        key_metrics_for_daily = [
            "Task Success Rate",
            "Autonomous Decision Rate",
            "Uptime Percentage",
            "Critical System Failure Rate",
            "Compute Unit Consumption"
        ]

        for metric_name in key_metrics_for_daily:
            metric = self.metrics_manager.get_metric(metric_name)
            if metric:
                summary = self._get_metric_summary(metric, start_time, end_time)
                report_lines.append(f"   - {metric.name}: Latest {summary['latest']}{summary['unit']} (Avg: {summary['average']}{summary['unit']})")
            else:
                report_lines.append(f"   - {metric_name}: Data N/A")

        report_lines.append("\n3. Resource Usage Trends (Brief):")
        report_lines.append("   - Overall resource utilization stable with minor fluctuations.")
        report_lines.append("\n4. Forecast for Next 24 Hours:")
        report_lines.append("   - Anticipate continued progress on current objectives. Monitoring for [Simulated: specific potential issue].")
        report_lines.append("--------------------------------------------------")

        return "\n".join(report_lines)

    def generate_weekly_report(self) -> str:
        """
        Generates a comprehensive weekly progress report.
        Content based on Section 3.2 of the design document.
        """
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=7)

        report_lines = [
            f"Weekly Progress Report - {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "--------------------------------------------------",
            "\n1. Executive Summary:",
            "   - This week saw [Simulated: significant progress on mission objectives/challenges in X area].",
            "   - Key achievements include [Simulated: completion of Y milestone, successful deployment of Z architectural change].",
            "   - Challenges encountered: [Simulated: brief network instability, unexpected resource spike].",
            "\n2. Detailed Metrics Analysis (Last 7 Days):"
        ]

        categories = sorted(list(set(m.category for m in self.metrics_manager.metrics.values())))
        for category in categories:
            report_lines.append(f"\n   --- {category} ---")
            metrics_in_category = self.metrics_manager.get_metrics_by_category(category)
            for metric_name, metric in metrics_in_category.items():
                summary = self._get_metric_summary(metric, start_time, end_time)
                report_lines.append(f"   - {metric.name}: Latest {summary['latest']}{summary['unit']} (Avg: {summary['average']}{summary['unit']})")
                # In a real system, you'd add trend analysis here (e.g., "up 5% from last week")

        report_lines.append("\n3. Architectural Changes & Adaptations:")
        report_lines.append("   - [Simulated: Implemented minor architectural adjustment for improved data processing efficiency].")
        report_lines.append("   - No major adaptations required this period.")

        report_lines.append("\n4. Identified Risks & Mitigation:")
        report_lines.append("   - Risk: Potential for increased energy consumption with new AI model deployments.")
        report_lines.append("   - Mitigation: Implementing dynamic power management protocols and monitoring 'Energy Consumption' closely.")

        report_lines.append("\n5. Key Insights for Planning:")
        report_lines.append("   - 'Knowledge Base Expansion Rate' shows healthy growth, suggesting effective learning processes.")
        report_lines.append("   - 'Adaptation Cycle Time' remains within acceptable limits, indicating efficient architectural evolution.")

        report_lines.append("\n6. Outlook for the Coming Week:")
        report_lines.append("   - Focus on [Simulated: optimizing resource allocation for upcoming computationally intensive tasks].")
        report_lines.append("   - Expect further refinements in 'Anomaly Resolution Rate' as new detection algorithms mature.")
        report_lines.append("--------------------------------------------------")

        return "\n".join(report_lines)

    def generate_on_demand_report(self, metric_name: str, days: int = 1) -> str:
        """
        Generates an on-demand report for a specific metric over a given number of days.
        """
        metric = self.metrics_manager.get_metric(metric_name)
        if not metric:
            return f"Error: Metric '{metric_name}' not found."

        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=days)
        values = metric.get_values_in_period(start_time, end_time)

        report_lines = [
            f"On-Demand Report for '{metric.name}' - Last {days} Day(s)",
            "--------------------------------------------------",
            f"Description: {metric.description}",
            f"Category: {metric.category}",
            f"Unit: {metric.unit if metric.unit else 'N/A'}",
            "\nRecorded Values (Timestamp, Value):"
        ]

        if not values:
            report_lines.append("   - No data recorded for this period.")
        else:
            for ts, val in values:
                report_lines.append(f"   - {ts.strftime('%Y-%m-%d %H:%M:%S')}: {val}{metric.unit}")
            numeric_values = [v for ts, v in values if isinstance(v, (int, float))]
            if numeric_values:
                report_lines.append(f"\nSummary:")
                report_lines.append(f"   - Latest Value: {values[-1][1]}{metric.unit}")
                report_lines.append(f"   - Average Value: {round(sum(numeric_values) / len(numeric_values), 2)}{metric.unit}")
                report_lines.append(f"   - Min Value: {min(numeric_values)}{metric.unit}")
                report_lines.append(f"   - Max Value: {max(numeric_values)}{metric.unit}")

        report_lines.append("--------------------------------------------------")
        return "\n".join(report_lines)


if __name__ == "__main__":
    # Initialize metrics and simulate some data
    metrics_manager = MetricsManager()
    # Adding a couple of metrics manually for a quick test
    metrics_manager.add_metric(Metric("Test Success Rate", "Test", "Dummy success rate.", unit="%"))
    metrics_manager.add_metric(Metric("Test Latency", "Test", "Dummy latency.", unit="ms"))

    now = datetime.datetime.now()
    for i in range(24): # 24 hourly data points
        timestamp = now - datetime.timedelta(hours=24 - i)
        metrics_manager.record_metric_value("Test Success Rate", random.uniform(0.8, 0.95), timestamp)
        metrics_manager.record_metric_value("Test Latency", random.uniform(50, 200), timestamp)

    # Simulate more realistic data using the initialize_metrics function
    full_metrics_manager = initialize_metrics()
    full_metrics_manager.simulate_data(num_days=8) # Simulate for more than 7 days for weekly report

    reporter = Reporter(full_metrics_manager)

    print("\n--- Generating Daily Report ---")
    daily_report = reporter.generate_daily_report()
    print(daily_report)

    print("\n--- Generating Weekly Report ---")
    weekly_report = reporter.generate_weekly_report()
    print(weekly_report)

    print("\n--- Generating On-Demand Report for 'Uptime Percentage' (last 3 days) ---")
    on_demand_report = reporter.generate_on_demand_report("Uptime Percentage", days=3)
    print(on_demand_report)
