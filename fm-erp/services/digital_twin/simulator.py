import simpy
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from .metrics import SimulationMetrics

@dataclass
class WarehouseConfig:
    skus: List[str]
    initial_stock: Dict[str, int]
    reorder_point: Dict[str, int]
    order_quantity: Dict[str, int]
    lead_time: Dict[str, int]
    demand_interval: float = 1.0
    avg_pick_time: float = 0.5
    holding_cost_rate: float = 0.1
    procurement_cost: float = 10.0
    stockout_penalty: float = 50.0
    safety_stock: Dict[str, int] = None

class WarehouseDTSimulator:
    """Digital Twin: Virtual replica of physical warehouse"""
    
    def __init__(self, config: WarehouseConfig, env: simpy.Environment):
        """
        Args:
            config: Warehouse parameters (SKUs, capacity, costs, demand patterns)
            env: SimPy discrete-event simulation environment
        """
        self.env = env
        self.config = config
        self.inventory = {sku: config.initial_stock.get(sku, 0) for sku in config.skus}
        self.orders = []
        self.metrics = SimulationMetrics()
        
    def run_simulation(self, duration_days: int = 365):
        """Run DES for specified duration, return metrics"""
        self.env.process(self.demand_generator())
        self.env.process(self.procurement_process())
        self.env.process(self.order_fulfillment_process())
        self.env.process(self.metrics_recorder())
        self.env.run(until=duration_days * 24 * 60)  # Convert to minutes
        return self.metrics.get_summary()
        
    def demand_generator(self):
        """Generate stochastic demand events"""
        while True:
            for sku in self.config.skus:
                # Sample from demand distribution (Poisson)
                demand_qty = np.random.poisson(5) # Simplified
                yield self.env.timeout(self.config.demand_interval)
                self._process_demand(sku, demand_qty)

    def _process_demand(self, sku, qty):
        self.orders.append({"sku": sku, "qty": qty})
                
    def procurement_process(self):
        """Procurement/replenishment process"""
        while True:
            for sku in self.config.skus:
                if self.inventory[sku] < self.config.reorder_point.get(sku, 0):
                    order_qty = self.config.order_quantity.get(sku, 100)
                    yield self.env.timeout(self.config.lead_time.get(sku, 1440)) # Default 1 day
                    self.inventory[sku] += order_qty
                    self.metrics.record_procurement(sku, order_qty, self.env.now)
            yield self.env.timeout(24 * 60)  # Check daily
            
    def order_fulfillment_process(self):
        """Order picking, packing, shipping workflow"""
        while True:
            if self.orders:
                order = self.orders.pop(0)
                # Simulate pick time (exponential distribution)
                pick_time = np.random.exponential(self.config.avg_pick_time)
                yield self.env.timeout(pick_time)
                # Check inventory availability
                if self._check_inventory_available(order):
                    self._fulfill_order(order)
                    self.metrics.record_fulfillment(order, self.env.now)
                else:
                    self.metrics.record_backorder(order, self.env.now)
            else:
                yield self.env.timeout(1) # Wait if no orders

    def metrics_recorder(self):
        while True:
            self.metrics.record_inventory_snapshot(self.env.now, self.inventory.copy())
            yield self.env.timeout(60) # Record every hour

    def _check_inventory_available(self, order):
        return self.inventory[order["sku"]] >= order["qty"]

    def _fulfill_order(self, order):
        self.inventory[order["sku"]] -= order["qty"]
    
    def get_inventory_state(self):
        return np.array([self.inventory[sku] for sku in sorted(self.config.skus)])
    
    def set_inventory_state(self, state_array):
        for i, sku in enumerate(sorted(self.config.skus)):
            self.inventory[sku] = state_array[i]
