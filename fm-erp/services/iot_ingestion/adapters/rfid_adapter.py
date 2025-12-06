import time
import json
from dataclasses import dataclass, asdict

@dataclass
class RFIDEvent:
    reader_id: str
    tag_epc: str
    sku: str
    quantity: int
    location: str
    timestamp: float
    signal_strength: float = 0.0

    def to_json(self):
        return json.dumps(asdict(self))

class IoTSensorAdapter:
    def __init__(self, producer):
        self.producer = producer

class RFIDAdapter(IoTSensorAdapter):
    """RFID reader adapter for inventory tracking"""
    
    def __init__(self, reader_id: str, location: str, 
                 kafka_producer):
        """
        Args:
            reader_id: Unique RFID reader identifier
            location: Physical location (e.g., "receiving_dock", "warehouse_zone_A")
            kafka_producer: Kafka producer for event streaming
        """
        super().__init__(kafka_producer)
        self.reader_id = reader_id
        self.location = location
        self.topic = "iot.rfid.events"
        
    def read_tag(self, tag_data: bytes) -> RFIDEvent:
        """
        Parse RFID tag and publish event
        
        Returns:
            RFIDEvent with SKU, quantity, timestamp, location
        """
        event = self._parse_epc_tag(tag_data)
        event.reader_id = self.reader_id
        event.location = self.location
        event.timestamp = time.time()
        
        # Publish to Kafka
        if self.producer:
            self.producer.send(self.topic, value=event.to_json().encode('utf-8'))
        
        return event
        
    def _parse_epc_tag(self, tag_data: bytes) -> RFIDEvent:
        """Parse EPC Gen2 tag format (96-bit)"""
        # Simplified parsing for prototype
        # Assume tag_data contains SKU and Quantity encoded
        decoded = tag_data.decode('utf-8')
        # Format: SKU:QTY
        parts = decoded.split(':')
        sku = parts[0]
        qty = int(parts[1]) if len(parts) > 1 else 1
        
        return RFIDEvent(
            reader_id=self.reader_id,
            tag_epc=decoded,
            sku=sku,
            quantity=qty,
            location=self.location,
            timestamp=time.time()
        )
