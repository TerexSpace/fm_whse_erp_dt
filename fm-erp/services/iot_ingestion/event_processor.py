import json
from .adapters.rfid_adapter import RFIDEvent
from .adapters.weight_scale_adapter import WeightEvent

class IoTEventProcessor:
    """Real-time processing of IoT sensor events"""
    
    def __init__(self, kafka_consumer, 
                 influxdb_client,
                 blockchain_adapter):
        self.consumer = kafka_consumer
        self.influxdb = influxdb_client
        self.blockchain = blockchain_adapter
        
    def process_events(self):
        """
        Main event processing loop:
        1. Consume events from Kafka
        2. Validate event integrity
        3. Store in InfluxDB (time-series)
        4. Submit critical events to blockchain
        5. Update digital twin state
        """
        if not self.consumer:
            return

        for message in self.consumer:
            event = self._deserialize_event(message.value)
            
            # Store in time-series database
            self._store_influxdb(event)
            
            # Check for critical events (threshold violations, anomalies)
            if self._is_critical(event):
                self._submit_to_blockchain(event)
                self._trigger_alert(event)
                
            # Update digital twin
            self._update_digital_twin(event)
            
    def _deserialize_event(self, value):
        # Simplified deserialization
        data = json.loads(value)
        if "tag_epc" in data:
            return RFIDEvent(**data)
        elif "weight" in data:
            return WeightEvent(**data)
        return data

    def _store_influxdb(self, event):
        if self.influxdb:
            self.influxdb.write_iot_event(event)

    def _submit_to_blockchain(self, event):
        if self.blockchain:
            # self.blockchain.submit_event(event)
            pass

    def _trigger_alert(self, event):
        pass

    def _update_digital_twin(self, event):
        pass

    def _is_critical(self, event) -> bool:
        """
        Determine if event requires blockchain recording
        """
        if isinstance(event, RFIDEvent):
            # Check if inventory count deviates from expected
            expected = self._get_expected_inventory(event.sku)
            actual = self._compute_actual_from_rfid(event)
            return abs(actual - expected) / expected > 0.05 if expected > 0 else False
            
        elif isinstance(event, WeightEvent):
            # Check shipment weight vs. manifest
            expected_weight = self._get_manifest_weight("SHIP-001")
            return abs(event.weight - expected_weight) / expected_weight > 0.02 if expected_weight > 0 else False
            
        return False

    def _get_expected_inventory(self, sku):
        return 100 # Mock

    def _compute_actual_from_rfid(self, event):
        return event.quantity

    def _get_manifest_weight(self, shipment_id):
        return 10.0 # Mock
