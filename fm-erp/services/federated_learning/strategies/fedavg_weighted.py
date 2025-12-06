import numpy as np
from typing import List, Tuple, Optional, Dict
import flwr as fl
from flwr.common import Parameters, Scalar, FitRes
from flwr.server.client_proxy import ClientProxy

class ByzantineRobustStrategy(fl.server.strategy.FedAvg):
    """
    Federated Averaging with Byzantine robustness (Krum/Median)
    """
    def __init__(self, 
                 min_fit_clients: int = 2,
                 min_available_clients: int = 2,
                 fraction_fit: float = 1.0,
                 fraction_evaluate: float = 1.0,
                 on_fit_config_fn = None,
                 on_evaluate_config_fn = None,
                 accept_failures: bool = True,
                 initial_parameters: Optional[Parameters] = None,
                 byzantine_tolerance: int = 0):
        
        super().__init__(
            min_fit_clients=min_fit_clients,
            min_available_clients=min_available_clients,
            fraction_fit=fraction_fit,
            fraction_evaluate=fraction_evaluate,
            on_fit_config_fn=on_fit_config_fn,
            on_evaluate_config_fn=on_evaluate_config_fn,
            accept_failures=accept_failures,
            initial_parameters=initial_parameters,
        )
        self.byzantine_tolerance = byzantine_tolerance

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[Tuple[ClientProxy, FitRes]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """Aggregate fit results using Krum or Median if specified."""
        
        if not results:
            return None, {}

        # Extract weights
        weights_results = [
            (fl.common.parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples)
            for _, fit_res in results
        ]
        
        # If byzantine tolerance is set, use Krum-like selection
        # For simplicity in this prototype, we'll implement a coordinate-wise median
        # which is robust to outliers.
        
        if self.byzantine_tolerance > 0:
            aggregated_ndarrays = self.coordinate_wise_median([w for w, _ in weights_results])
        else:
            # Default FedAvg
            aggregated_ndarrays = fl.server.strategy.aggregate.aggregate(weights_results)

        parameters_aggregated = fl.common.ndarrays_to_parameters(aggregated_ndarrays)

        # Aggregate custom metrics if aggregation_fn is provided
        metrics_aggregated = {}
        
        return parameters_aggregated, metrics_aggregated

    def coordinate_wise_median(self, weights_list: List[List[np.ndarray]]) -> List[np.ndarray]:
        """
        Compute coordinate-wise median of weights.
        weights_list: List of client weights, where each client weight is a list of ndarrays (layers)
        """
        # Transpose to get list of layers, where each layer contains arrays from all clients
        num_layers = len(weights_list[0])
        aggregated_layers = []
        
        for layer_idx in range(num_layers):
            # Stack weights for this layer from all clients: [num_clients, shape...]
            layer_weights = [client_weights[layer_idx] for client_weights in weights_list]
            stacked = np.stack(layer_weights, axis=0)
            median_layer = np.median(stacked, axis=0)
            aggregated_layers.append(median_layer)
            
        return aggregated_layers

    def krum_aggregation(self, weights_list: List[List[np.ndarray]], num_byzantine: int) -> List[np.ndarray]:
        """
        Krum algorithm: Select gradient closest to majority
        (Placeholder for full implementation)
        """
        # Simplified selection of the first non-malicious looking update
        # In a real implementation, this would compute pairwise distances
        return weights_list[0] 

class FedAvgAggregator:
    """Standard FedAvg Aggregation"""
    def aggregate(self, gradients: List[np.ndarray], weights: List[int]) -> np.ndarray:
        """Compute weighted average of gradients"""
        total_weight = sum(weights)
        weighted_sum = sum(w * g for w, g in zip(weights, gradients))
        return weighted_sum / total_weight

class KrumSelector:
    """Krum Byzantine Tolerance Algorithm"""
    def __init__(self, num_byzantine: int):
        self.num_byzantine = num_byzantine
        
    def select(self, gradients: List[np.ndarray]) -> np.ndarray:
        """Select the gradient that minimizes sum of distances to k nearest neighbors"""
        n = len(gradients)
        f = self.num_byzantine
        k = n - f - 2
        
        if k < 0:
            # Fallback if not enough clients
            return gradients[0]
            
        scores = []
        for i in range(n):
            dists = []
            for j in range(n):
                if i == j: continue
                dist = np.linalg.norm(gradients[i] - gradients[j])
                dists.append(dist)
            
            dists.sort()
            score = sum(dists[:k])
            scores.append(score)
            
        best_idx = np.argmin(scores)
        return gradients[best_idx]

class GaussianDPMechanism:
    """Differential Privacy Mechanism"""
    def __init__(self, epsilon: float, delta: float, sensitivity: float):
        self.epsilon = epsilon
        self.delta = delta
        self.sensitivity = sensitivity
        
    def add_noise(self, gradient: np.ndarray) -> np.ndarray:
        """Add Gaussian noise for (epsilon, delta)-DP"""
        sigma = self.sensitivity * np.sqrt(2 * np.log(1.25/self.delta)) / self.epsilon
        noise = np.random.normal(0, sigma, gradient.shape)
        return gradient + noise
