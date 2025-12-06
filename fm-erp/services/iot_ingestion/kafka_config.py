KAFKA_CONFIG = {
    "bootstrap_servers": ["localhost:9092"],
    "topics": {
        "iot.rfid.events": {
            "partitions": 3,
            "replication_factor": 2,
            "retention_ms": 604800000,  # 7 days
            "compression_type": "snappy"
        },
        "iot.barcode.events": {
            "partitions": 2,
            "replication_factor": 2,
            "retention_ms": 604800000
        },
        "iot.weight.events": {
            "partitions": 1,
            "replication_factor": 2,
            "retention_ms": 2592000000  # 30 days (for audit)
        },
        "iot.alerts": {
            "partitions": 1,
            "replication_factor": 3,
            "retention_ms": 31536000000  # 1 year
        }
    }
}

class IoTEventSchema:
    """Avro schema for IoT events (ensures compatibility)"""
    
    RFID_EVENT_SCHEMA = {
        "type": "record",
        "name": "RFIDEvent",
        "fields": [
            {"name": "reader_id", "type": "string"},
            {"name": "tag_epc", "type": "string"},
            {"name": "sku", "type": "string"},
            {"name": "quantity", "type": "int"},
            {"name": "location", "type": "string"},
            {"name": "timestamp", "type": "long"},  # Unix timestamp (ms)
            {"name": "signal_strength", "type": "float"}
        ]
    }
