from typing import Dict, Optional
import numpy as np

class SimulationResults:
    def __init__(self):
        self.inventory_history = {} # node_id -> {timestamp -> (actual, system)}
        self.order_history = {"fulfillment_time_hours": []}
        self.consensus_latencies = []
        self.total_local_data_mb = 1000.0
        self.shared_data_mb = 10.0

class MetricsCollector:
    """Collects and computes evaluation metrics from simulation results"""
    
    def compute_all_metrics(self, simulation_results: SimulationResults, 
                           baseline_results: Optional[SimulationResults] = None) -> Dict[str, float]:
        """
        Compute all metrics defined in JUCS manuscript Section 5.3
        
        Returns:
            Dictionary with metric_name: value pairs
        """
        metrics = {}
        
        # Primary Metrics (from Table 1 in JUCS manuscript)
        metrics["IDR"] = self._compute_inventory_discrepancy_rate(simulation_results)
        metrics["OFT"] = self._compute_order_fulfillment_time(simulation_results)
        metrics["CL"] = self._compute_consensus_latency(simulation_results)
        metrics["TPS"] = self._compute_throughput(simulation_results)
        metrics["PP"] = self._compute_privacy_preservation(simulation_results)
        
        # Operational Cost Reduction (requires baseline)
        if baseline_results:
            metrics["OCR"] = self._compute_operational_cost_reduction(
                simulation_results, baseline_results
            )
        
        # Secondary Metrics
        metrics["MAPE"] = self._compute_demand_forecast_accuracy(simulation_results)
        metrics["sync_frequency"] = self._compute_dt_sync_frequency(simulation_results)
        metrics["communication_overhead_mb"] = self._compute_communication_overhead(simulation_results)
        
        return metrics
        
    def _compute_inventory_discrepancy_rate(self, results: SimulationResults) -> float:
        """
        IDR = (1/NT) Σ Σ |s_actual - s_system| / s_actual
        
        From JUCS manuscript Equation (Section 5.3)
        """
        total_discrepancy = 0
        total_observations = 0
        
        for node_id, node_data in results.inventory_history.items():
            for timestamp, (actual, system) in node_data.items():
                discrepancy = np.abs(actual - system) / (actual + 1e-10)  # Avoid division by zero
                total_discrepancy += np.sum(discrepancy)
                total_observations += len(actual)
        
        if total_observations == 0:
            return 0.0

        idr = total_discrepancy / total_observations
        return idr * 100  # Return as percentage
        
    def _compute_order_fulfillment_time(self, results: SimulationResults) -> float:
        """Mean time from order placement to shipment (hours)"""
        fulfillment_times = results.order_history["fulfillment_time_hours"]
        if not fulfillment_times:
            return 0.0
        return np.mean(fulfillment_times)
        
    def _compute_consensus_latency(self, results: SimulationResults) -> float:
        """Mean blockchain consensus finality time (seconds)"""
        if not results.consensus_latencies:
            return np.nan  # N/A for non-blockchain systems
        return np.mean(results.consensus_latencies)
        
    def _compute_privacy_preservation(self, results: SimulationResults) -> float:
        """
        PP = (1 - shared_data / total_data) * 100%
        
        For FM-ERP: Only aggregated gradients/fitness values shared
        """
        total_data_size = results.total_local_data_mb
        shared_data_size = results.shared_data_mb  # Gradients, fitness hashes
        
        if total_data_size == 0:
            return 100.0

        pp = (1 - shared_data_size / total_data_size) * 100
        return pp

    def _compute_throughput(self, results):
        return 100.0 # Mock

    def _compute_operational_cost_reduction(self, results, baseline):
        return 10.0 # Mock

    def _compute_demand_forecast_accuracy(self, results):
        return 10.0 # Mock MAPE

    def _compute_dt_sync_frequency(self, results):
        return 5.0 # Mock

    def _compute_communication_overhead(self, results):
        return 50.0 # Mock
