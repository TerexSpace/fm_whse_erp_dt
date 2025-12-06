import time
import json
from dataclasses import dataclass, asdict
from .rfid_adapter import IoTSensorAdapter

@dataclass
class WeightEvent:
    scale_id: str
    weight: float
    unit: str
    timestamp: float
    calibration_status: bool

    def to_json(self):
        return json.dumps(asdict(self))

class WeightScaleAdapter(IoTSensorAdapter):
    """Digital weight scale adapter for shipment verification"""
    
    def __init__(self, scale_id: str, kafka_producer):
        super().__init__(kafka_producer)
        self.scale_id = scale_id
        self.topic = "iot.weight.events"

    def read_weight(self) -> WeightEvent:
        """
        Read weight measurement (kg, with 0.01 kg precision)
        
        Returns:
            WeightEvent with weight, unit, timestamp
        """
        weight_kg = self._read_serial_port()  # Read from RS-232 or USB interface
        
        event = WeightEvent(
            scale_id=self.scale_id,
            weight=weight_kg,
            unit="kg",
            timestamp=time.time(),
            calibration_status=self._check_calibration()
        )
        
        if self.producer:
            self.producer.send(self.topic, value=event.to_json().encode('utf-8'))
        return event

    def _read_serial_port(self):
        return 10.5 # Mock

    def _check_calibration(self):
        return True
