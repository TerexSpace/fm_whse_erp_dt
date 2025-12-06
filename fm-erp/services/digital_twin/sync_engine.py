import time
import numpy as np
from .simulator import WarehouseDTSimulator

class DTSynchronizer:
    """Synchronizes digital twin with physical warehouse via IoT sensors"""
    
    def __init__(self, dt_simulator: WarehouseDTSimulator, 
                 iot_adapter=None,
                 blockchain_adapter=None):
        self.dt = dt_simulator
        self.iot = iot_adapter
        self.blockchain = blockchain_adapter
        self.sync_threshold = 0.05  # 5% discrepancy threshold
        
    def sync_state(self, force: bool = False):
        """
        Synchronize DT state with physical sensors
        """
        if not self.iot:
            return {"synced": False, "reason": "No IoT adapter"}

        physical_state = self.iot.get_current_inventory()
        virtual_state = self.dt.get_inventory_state()
        
        discrepancy = self._compute_discrepancy(physical_state, virtual_state)
        
        if discrepancy > self.sync_threshold or force:
            # Submit to blockchain for verification
            sync_tx = {
                "function": "SyncDigitalTwin",
                "args": [physical_state.tolist(), discrepancy, time.time()]
            }
            
            consensus_result = {"success": True}
            if self.blockchain:
                consensus_result = self.blockchain.invoke_chaincode(sync_tx)
            
            if consensus_result["success"]:
                self.dt.set_inventory_state(physical_state)
                return {"synced": True, "discrepancy": discrepancy}
        
        return {"synced": False, "discrepancy": discrepancy}
        
    def _compute_discrepancy(self, physical: np.ndarray, 
                            virtual: np.ndarray) -> float:
        """L2 relative error: ||physical - virtual|| / ||physical||"""
        norm_physical = np.linalg.norm(physical)
        if norm_physical == 0:
            return 0.0 if np.linalg.norm(virtual) == 0 else 1.0
        return np.linalg.norm(physical - virtual) / norm_physical
