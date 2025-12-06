import pytest
import simpy
import numpy as np
from services.digital_twin.simulator import WarehouseDTSimulator, WarehouseConfig
from services.digital_twin.inventory_manager import InventoryStateManager, InsufficientInventoryError
from services.digital_twin.sync_engine import DTSynchronizer

class MockIoTAdapter:
    def get_current_inventory(self):
        return np.array([100, 200])

class TestDigitalTwin:
    
    def test_inventory_manager(self):
        """Test inventory state management"""
        manager = InventoryStateManager(["SKU1"], {"SKU1": 10})
        manager.update_inventory("SKU1", 5, "procurement", 100.0)
        assert manager.inventory["SKU1"] == 15
        
        with pytest.raises(InsufficientInventoryError):
            manager.update_inventory("SKU1", -20, "demand", 101.0)

    def test_simulator_run(self):
        """Test basic simulation run"""
        env = simpy.Environment()
        config = WarehouseConfig(
            skus=["SKU1"],
            initial_stock={"SKU1": 100},
            reorder_point={"SKU1": 50},
            order_quantity={"SKU1": 100},
            lead_time={"SKU1": 10}
        )
        simulator = WarehouseDTSimulator(config, env)
        metrics = simulator.run_simulation(duration_days=1)
        
        assert metrics["avg_inventory"] > 0

    def test_synchronization(self):
        """Test DT synchronization logic"""
        env = simpy.Environment()
        config = WarehouseConfig(
            skus=["SKU1", "SKU2"],
            initial_stock={"SKU1": 100, "SKU2": 200},
            reorder_point={},
            order_quantity={},
            lead_time={}
        )
        simulator = WarehouseDTSimulator(config, env)
        
        # Mock IoT adapter returning same state
        iot = MockIoTAdapter()
        
        sync = DTSynchronizer(simulator, iot_adapter=iot)
        result = sync.sync_state()
        
        assert result["discrepancy"] == 0.0
        assert not result["synced"] # No sync needed
        
        # Change simulator state to create discrepancy
        simulator.inventory["SKU1"] = 50
        result = sync.sync_state()
        
        assert result["discrepancy"] > 0.0
        assert result["synced"] # Should sync
        assert simulator.inventory["SKU1"] == 100 # Restored
