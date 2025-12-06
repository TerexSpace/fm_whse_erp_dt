from typing import Dict, List

class SimulationMetrics:
    """Collects and aggregates DT simulation metrics"""
    
    def __init__(self):
        self.inventory_history = []
        self.order_history = []
        self.stockout_events = []
        self.procurement_events = []
        self.total_procurements = 0
        self.stockout_incidents = 0
        self.avg_inventory = 0.0
        
    def record_inventory_snapshot(self, timestamp: float, state: Dict[str, int]):
        """Record inventory levels at timestamp"""
        self.inventory_history.append({"time": timestamp, "state": state})
        
    def record_procurement(self, sku: str, quantity: int, timestamp: float):
        self.procurement_events.append({"sku": sku, "qty": quantity, "time": timestamp})
        self.total_procurements += 1
        
    def record_fulfillment(self, order, timestamp: float):
        self.order_history.append({"order": order, "time": timestamp, "status": "fulfilled"})
        
    def record_backorder(self, order, timestamp: float):
        self.stockout_events.append({"order": order, "time": timestamp})
        self.stockout_incidents += 1
        
    def get_summary(self):
        # Calculate average inventory
        if self.inventory_history:
            total_items = sum(sum(record["state"].values()) for record in self.inventory_history)
            self.avg_inventory = total_items / len(self.inventory_history)
            
        return {
            "avg_inventory": self.avg_inventory,
            "total_procurements": self.total_procurements,
            "stockout_incidents": self.stockout_incidents
        }
