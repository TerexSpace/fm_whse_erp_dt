import time
from typing import Optional
from dataclasses import dataclass

@dataclass
class Anomaly:
    event: object
    z_score: float
    severity: str
    timestamp: float

class IoTAnomalyDetector:
    """Detect anomalies in IoT sensor streams"""
    
    def __init__(self, sensitivity: float = 3.0):
        """
        Args:
            sensitivity: Number of standard deviations for anomaly threshold
        """
        self.sensitivity = sensitivity
        self.baseline_stats = {}  # Store mean/std for each sensor
        
    def detect_anomaly(self, event) -> Optional[Anomaly]:
        """
        Z-score anomaly detection:
        z = (x - μ) / σ
        Flag if |z| > sensitivity
        
        Returns:
            Anomaly object if detected, None otherwise
        """
        if not hasattr(event, 'value') and not hasattr(event, 'weight'):
             return None

        val = getattr(event, 'value', getattr(event, 'weight', 0))
        sensor_id = getattr(event, 'sensor_id', getattr(event, 'scale_id', 'unknown'))
        metric_name = "value"

        sensor_key = f"{sensor_id}_{metric_name}"
        
        if sensor_key not in self.baseline_stats:
            # Initialize baseline from historical data
            self._compute_baseline(sensor_key)
            
        stats = self.baseline_stats[sensor_key]
        if stats['std'] == 0:
            return None

        z_score = (val - stats['mean']) / stats['std']
        
        if abs(z_score) > self.sensitivity:
            return Anomaly(
                event=event,
                z_score=z_score,
                severity="high" if abs(z_score) > 5.0 else "medium",
                timestamp=time.time()
            )
            
        return None

    def _compute_baseline(self, sensor_key):
        # Mock baseline
        self.baseline_stats[sensor_key] = {'mean': 10.0, 'std': 0.1}
