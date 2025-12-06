from typing import List, Dict
import numpy as np

class InsufficientInventoryError(Exception):
    pass

class InventoryStateManager:
    """Manages inventory state transitions in digital twin"""
    
    def __init__(self, skus: List[str], initial_stock: Dict[str, int]):
        self.inventory = {sku: initial_stock.get(sku, 0) for sku in skus}
        self.transaction_log = []
        
    def update_inventory(self, sku: str, delta: int, 
                        transaction_type: str, timestamp: float):
        """
        Update inventory level with transaction logging
        
        Args:
            sku: Stock-keeping unit ID
            delta: Change in inventory (positive=addition, negative=consumption)
            transaction_type: 'procurement', 'demand', 'transfer_in', 'transfer_out'
            timestamp: Simulation time of transaction
        """
        if self.inventory[sku] + delta < 0:
            raise InsufficientInventoryError(f"SKU {sku}: {self.inventory[sku]} + {delta} < 0")
        
        self.inventory[sku] += delta
        self.transaction_log.append({
            "sku": sku,
            "delta": delta,
            "type": transaction_type,
            "timestamp": timestamp,
            "balance": self.inventory[sku]
        })
        
    def get_state_vector(self) -> np.ndarray:
        """Return current inventory state as vector for ML input"""
        return np.array([self.inventory[sku] for sku in sorted(self.inventory.keys())])
