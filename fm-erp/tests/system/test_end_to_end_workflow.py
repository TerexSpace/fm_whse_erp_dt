import pytest
from experiments.experiment_config import ExperimentConfig
from experiments.orchestrator import ExperimentOrchestrator
from unittest.mock import Mock

class FMERPSystem:
    def __init__(self, num_nodes, config):
        self.num_nodes = num_nodes
        self.config = config
        self.blockchain_adapter = Mock()
    
    def start(self): pass
    def ingest_iot_data(self, data): pass
    def start_fl_training_round(self): return "round_1"
    def wait_for_fl_completion(self, round_id, timeout): pass
    def get_digital_twin_state(self): 
        state = Mock()
        state.inventory_accuracy = 0.96
        return state
    def optimize_resource_allocation(self):
        res = Mock()
        res.converged = True
        res.iterations = 50
        res.blockchain_transaction_id = "tx_opt_1"
        return res
    def compute_metrics(self):
        return {"IDR": 5.0, "OFT": 2.0, "PP": 99.5}

class IoTDataSimulator:
    def __init__(self, num_sensors): pass
    def generate_hourly_data(self): return []

@pytest.mark.slow
@pytest.mark.system
class TestEndToEndWorkflow:
    """System tests: Complete FM-ERP workflows"""
    
    def test_complete_federated_optimization_workflow(self):
        """
        Test full workflow:
        1. IoT sensors generate inventory data
        2. Digital twin simulates warehouse state
        3. FL trains demand forecasting model
        4. AQPSO-BV optimizes resource allocation
        5. Blockchain records optimization results
        """
        # Step 1: Initialize FM-ERP system
        fm_erp = FMERPSystem(
            num_nodes=15,
            config=ExperimentConfig(experiment_id="test", name="test", description="test", system="FM-ERP", random_seed=42)
        )
        fm_erp.start()
        
        # Step 2: Simulate IoT data for 24 hours
        iot_simulator = IoTDataSimulator(num_sensors=50)
        for hour in range(24):
            sensor_data = iot_simulator.generate_hourly_data()
            fm_erp.ingest_iot_data(sensor_data)
            
        # Step 3: Trigger federated learning round
        fl_round_id = fm_erp.start_fl_training_round()
        fm_erp.wait_for_fl_completion(fl_round_id, timeout=300)
        
        # Step 4: Run digital twin simulation
        dt_state = fm_erp.get_digital_twin_state()
        assert dt_state.inventory_accuracy > 0.95  # >95% DT accuracy
        
        # Step 5: Optimize allocation via AQPSO-BV
        optimization_result = fm_erp.optimize_resource_allocation()
        assert optimization_result.converged == True
        assert optimization_result.iterations < 100
        
        # Step 6: Verify blockchain recorded results
        tx_id = optimization_result.blockchain_transaction_id
        
        fm_erp.blockchain_adapter.query_transaction.return_value = {
            "status": "COMMITTED",
            "consensus_reached": True
        }
        
        blockchain_record = fm_erp.blockchain_adapter.query_transaction(tx_id)
        assert blockchain_record["status"] == "COMMITTED"
        assert blockchain_record["consensus_reached"] == True
        
        # Step 7: Validate final metrics
        metrics = fm_erp.compute_metrics()
        assert metrics["IDR"] < 10.0  # Inventory discrepancy < 10%
        assert metrics["OFT"] < 3.0  # Order fulfillment < 3 hours
        assert metrics["PP"] > 99.0  # Privacy preservation > 99%
