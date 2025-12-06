import numpy as np
from dataclasses import dataclass
from typing import List
from .experiment_config import ExperimentConfig

@dataclass
class WarehouseData:
    node_id: int
    warehouse_type: str
    num_skus: int
    capacity: int
    demand_patterns: np.ndarray
    holding_cost: np.ndarray
    procurement_cost: np.ndarray
    transfer_cost: np.ndarray

class SyntheticWarehouseDataGenerator:
    """Generates synthetic multi-SME warehouse datasets"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        np.random.seed(config.random_seed)
        
    def generate_dataset(self) -> List[WarehouseData]:
        """
        Generate datasets for N SME warehouses
        
        Returns:
            List of WarehouseData objects (one per SME node)
        """
        warehouses = []
        
        for node_id in range(self.config.num_sme_nodes):
            # Sample warehouse type (retail, manufacturing, logistics)
            warehouse_type = np.random.choice(
                ["retail", "manufacturing", "logistics"],
                p=[0.33, 0.33, 0.34]
            )
            
            # Generate warehouse parameters
            warehouse = self._generate_warehouse(node_id, warehouse_type)
            warehouses.append(warehouse)
            
        return warehouses
        
    def _generate_warehouse(self, node_id: int, 
                           warehouse_type: str) -> WarehouseData:
        """Generate individual warehouse with type-specific characteristics"""
        
        # Number of SKUs (type-dependent)
        if warehouse_type == "retail":
            num_skus = np.random.randint(200, 500)  # High-volume, high-variety
        elif warehouse_type == "manufacturing":
            num_skus = np.random.randint(50, 200)   # Medium-volume
        else:  # logistics
            num_skus = np.random.randint(100, 300)  # Mixed
            
        # Storage capacity (log-normal distribution)
        capacity = int(np.random.lognormal(mean=8, sigma=1.5))  # Pallet positions
        
        # Generate demand patterns
        demand_patterns = self._generate_demand_patterns(
            num_skus, warehouse_type, self.config.simulation_days
        )
        
        # Costs
        holding_cost = np.random.uniform(1, 5, num_skus)  # $/unit/day
        procurement_cost = np.random.uniform(10, 100, num_skus)  # $/unit
        transfer_cost = np.random.uniform(5, 20, num_skus)  # $/unit
        
        return WarehouseData(
            node_id=node_id,
            warehouse_type=warehouse_type,
            num_skus=num_skus,
            capacity=capacity,
            demand_patterns=demand_patterns,
            holding_cost=holding_cost,
            procurement_cost=procurement_cost,
            transfer_cost=transfer_cost
        )
        
    def _generate_demand_patterns(self, num_skus: int, 
                                  warehouse_type: str,
                                  num_days: int) -> np.ndarray:
        """
        Generate time-series demand patterns
        
        Returns:
            Array of shape [num_skus, num_days * 24] (hourly demand)
        """
        demand = np.zeros((num_skus, num_days * 24))
        
        for sku_id in range(num_skus):
            if warehouse_type == "retail":
                # Seasonal Poisson demand
                base_rate = np.random.uniform(10, 100)  # Units per day
                seasonal_pattern = self._seasonal_pattern(num_days)
                hourly_rate = (base_rate / 24) * seasonal_pattern
                demand[sku_id, :] = np.random.poisson(hourly_rate)
                
            elif warehouse_type == "manufacturing":
                # Steady-state demand (low variability)
                base_rate = np.random.uniform(5, 50)
                demand[sku_id, :] = np.random.poisson(base_rate / 24, num_days * 24)
                
            else:  # logistics
                # Bursty demand (Pareto distribution)
                alpha = 1.5  # Shape parameter (heavy tail)
                scale = np.random.uniform(1, 10)
                demand[sku_id, :] = np.random.pareto(alpha, num_days * 24) * scale
                
        return demand
        
    def _seasonal_pattern(self, num_days: int) -> np.ndarray:
        """Generate seasonal multiplier: 1 + 0.3*sin(2π*t/365)"""
        t = np.arange(num_days * 24) / 24  # Convert to days
        pattern = 1 + 0.3 * np.sin(2 * np.pi * t / 365)
        return np.repeat(pattern, 1)  # Broadcast to hourly
