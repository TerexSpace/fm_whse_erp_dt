from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import copy

@dataclass
class ExperimentConfig:
    """Configuration for reproducible experiments"""
    
    # Experiment identification
    experiment_id: str
    name: str
    description: str
    
    # System under test
    system: str  # "FM-ERP", "Baseline-Centralized", "Baseline-FL", etc.
    
    # Warehouse parameters
    num_sme_nodes: int = 15
    num_skus_per_node: Tuple[int, int] = (50, 500)  # (min, max) uniform distribution
    simulation_days: int = 365
    
    # Data generation
    random_seed: int = 42
    demand_distribution: str = "seasonal_poisson"  # or "pareto", "steady_state"
    demand_variability: float = 0.3  # CV = σ/μ
    
    # Algorithm hyperparameters
    fl_config: Dict = field(default_factory=lambda: {
        "num_rounds": 200,
        "local_epochs": 5,
        "learning_rate": 0.01,
        "batch_size": 32
    })
    
    aqpso_config: Dict = field(default_factory=lambda: {
        "num_particles": 30,
        "max_iterations": 100,
        "beta": 1.0,
        "quantum_probability": 0.1
    })
    
    # Evaluation metrics
    metrics: List[str] = field(default_factory=lambda: [
        "inventory_discrepancy_rate",
        "order_fulfillment_time",
        "operational_cost_reduction",
        "consensus_latency",
        "throughput_tps",
        "privacy_preservation"
    ])
    
    # Output
    output_dir: str = "experiments/results/"
    save_checkpoints: bool = True
    checkpoint_interval: int = 50  # Save every 50 iterations


BASELINE_CONFIGS = {
    "Baseline-Centralized": {
        "blockchain": False,
        "federated_learning": False,
        "digital_twin": False,
        "optimization_algorithm": "cplex"
    },
    "Baseline-Blockchain": {
        "blockchain": True,
        "consensus": "pbft",
        "federated_learning": False,
        "digital_twin": False,
        "optimization_algorithm": "standard_pso"
    },
    "Baseline-FL": {
        "blockchain": False,
        "federated_learning": True,
        "fl_algorithm": "fedavg",
        "digital_twin": False,
        "optimization_algorithm": "gradient_descent"
    },
    "Baseline-DT": {
        "blockchain": False,
        "federated_learning": False,
        "digital_twin": True,
        "optimization_algorithm": "genetic_algorithm"
    },
    "FM-ERP": {
        "blockchain": True,
        "consensus": "podq",
        "federated_learning": True,
        "fl_algorithm": "fedavg_byzantine_robust",
        "digital_twin": True,
        "optimization_algorithm": "aqpso_bv"
    }
}
