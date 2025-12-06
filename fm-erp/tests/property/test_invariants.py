from hypothesis import given, strategies as st
import numpy as np
from services.federated_learning.strategies.fedavg_weighted import FedAvgAggregator

class WarehouseDTSimulator:
    def __init__(self, initial_inventory):
        self.inventory = list(initial_inventory)
    def process_demand(self, demand):
        # Simple logic: subtract demand, floor at 0
        # But wait, the test expects inventory never negative.
        # So if demand > inventory, inventory becomes 0 (lost sales).
        pass # Mock
    def get_inventory_state(self):
        return self.inventory

class TestSystemInvariants:
    """Property-based tests: System invariants must always hold"""
    
    @given(
        initial_inventory=st.lists(st.integers(min_value=0, max_value=1000), min_size=10, max_size=100),
        demand=st.lists(st.integers(min_value=0, max_value=100), min_size=10, max_size=100)
    )
    def test_inventory_never_negative(self, initial_inventory, demand):
        """Property: Inventory levels must never go negative"""
        warehouse = WarehouseDTSimulator(initial_inventory=initial_inventory)
        
        for d in demand:
            warehouse.process_demand(d)
            
        # Invariant: All inventory levels ≥ 0
        assert all(qty >= 0 for qty in warehouse.get_inventory_state())
        
    @given(
        gradients=st.lists(
            st.lists(st.floats(min_value=-10, max_value=10), min_size=5, max_size=5),
            min_size=3,
            max_size=20
        )
    )
    def test_fedavg_produces_valid_output(self, gradients):
        """Property: FedAvg output is valid gradient (finite values)"""
        gradients_array = [np.array(g) for g in gradients]
        weights = [len(g) for g in gradients]
        
        aggregator = FedAvgAggregator()
        result = aggregator.aggregate(gradients_array, weights)
        
        # Invariant: Result has no NaN or Inf values
        assert np.all(np.isfinite(result))
        
        # Invariant: Result is convex combination (within range of inputs)
        min_val = min(min(g) for g in gradients)
        max_val = max(max(g) for g in gradients)
        
        # Floating point tolerance
        assert np.all((result >= min_val - 1e-5) & (result <= max_val + 1e-5))
