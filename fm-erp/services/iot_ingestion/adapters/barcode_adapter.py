import time
import json
from dataclasses import dataclass, asdict
from .rfid_adapter import IoTSensorAdapter

@dataclass
class BarcodeEvent:
    barcode: str
    sku: str
    scanner_id: str
    operator_id: str
    timestamp: float

    def to_json(self):
        return json.dumps(asdict(self))

class BarcodeAdapter(IoTSensorAdapter):
    """Barcode scanner adapter for manual scanning operations"""
    
    def __init__(self, scanner_id: str, kafka_producer):
        super().__init__(kafka_producer)
        self.scanner_id = scanner_id
        self.topic = "iot.barcode.events"

    def scan_barcode(self, barcode: str) -> BarcodeEvent:
        """
        Process scanned barcode (UPC-A, EAN-13, Code 128, QR)
        
        Returns:
            BarcodeEvent with SKU, operator_id, timestamp
        """
        event = BarcodeEvent(
            barcode=barcode,
            sku=self._lookup_sku(barcode),
            scanner_id=self.scanner_id,
            operator_id=self._get_current_operator(),
            timestamp=time.time()
        )
        
        if self.producer:
            self.producer.send(self.topic, value=event.to_json().encode('utf-8'))
        return event

    def _lookup_sku(self, barcode):
        # Mock lookup
        return f"SKU-{barcode}"

    def _get_current_operator(self):
        return "OP-001"
