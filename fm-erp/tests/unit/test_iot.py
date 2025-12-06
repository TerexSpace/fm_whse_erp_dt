import pytest
from services.iot_ingestion.adapters.rfid_adapter import RFIDAdapter
from services.iot_ingestion.adapters.barcode_adapter import BarcodeAdapter
from services.iot_ingestion.adapters.weight_scale_adapter import WeightScaleAdapter
from services.iot_ingestion.event_processor import IoTEventProcessor
from services.iot_ingestion.anomaly_detector import IoTAnomalyDetector

class MockProducer:
    def __init__(self):
        self.messages = []
    def send(self, topic, value):
        self.messages.append((topic, value))

class TestIoT:
    
    def test_rfid_adapter(self):
        producer = MockProducer()
        adapter = RFIDAdapter("READER-01", "DOCK-A", producer)
        
        event = adapter.read_tag(b"SKU-123:50")
        
        assert event.sku == "SKU-123"
        assert event.quantity == 50
        assert len(producer.messages) == 1
        assert producer.messages[0][0] == "iot.rfid.events"

    def test_barcode_adapter(self):
        producer = MockProducer()
        adapter = BarcodeAdapter("SCANNER-01", producer)
        
        event = adapter.scan_barcode("123456789")
        
        assert event.sku == "SKU-123456789"
        assert len(producer.messages) == 1

    def test_weight_adapter(self):
        producer = MockProducer()
        adapter = WeightScaleAdapter("SCALE-01", producer)
        
        event = adapter.read_weight()
        
        assert event.weight == 10.5
        assert len(producer.messages) == 1

    def test_anomaly_detection(self):
        detector = IoTAnomalyDetector(sensitivity=2.0)
        
        # Normal event (mean=10, std=0.1)
        producer = MockProducer()
        adapter = WeightScaleAdapter("SCALE-01", producer)
        normal_event = adapter.read_weight() # 10.5 -> z=5 (Anomaly!)
        
        # Wait, 10.5 with mean 10 and std 0.1 is (10.5-10)/0.1 = 5.0. That IS an anomaly.
        anomaly = detector.detect_anomaly(normal_event)
        assert anomaly is not None
        assert anomaly.severity == "medium" # 5.0 is not > 5.0 strictly? code says > 5.0 is high. 5.0 is medium.

    def test_event_processor_critical(self):
        processor = IoTEventProcessor(None, None, None)
        
        # Critical weight event
        producer = MockProducer()
        adapter = WeightScaleAdapter("SCALE-01", producer)
        event = adapter.read_weight() # 10.5 vs expected 10.0 -> 5% diff > 2% threshold
        
        assert processor._is_critical(event) == True
