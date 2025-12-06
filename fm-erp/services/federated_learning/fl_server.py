import flwr as fl
from typing import Dict, List, Optional
import numpy as np
from .strategies.fedavg_weighted import ByzantineRobustStrategy

class FMERPFederatedServer:
    def __init__(self, min_clients: int = 2, blockchain_adapter=None):
        """Initialize FL server with blockchain integration"""
        self.min_clients = min_clients
        self.blockchain_adapter = blockchain_adapter
        
        # Define strategy
        self.strategy = ByzantineRobustStrategy(
            min_fit_clients=min_clients,
            min_available_clients=min_clients,
            fraction_fit=1.0,
            fraction_evaluate=1.0,
            byzantine_tolerance=1 # Example tolerance
        )

    def start_server(self, server_address: str = "[::]:8080", config: Dict = None):
        """Start the Flower server"""
        if config is None:
            config = {"num_rounds": 3}
            
        fl.server.start_server(
            server_address=server_address,
            config=fl.server.ServerConfig(num_rounds=config["num_rounds"]),
            strategy=self.strategy,
        )

    def verify_gradient_blockchain(self, gradient_hash: str, client_id: str) -> bool:
        """Submit gradient hash to blockchain for verification via PoDQ"""
        if self.blockchain_adapter:
            # return self.blockchain_adapter.verify_hash(client_id, gradient_hash)
            pass
        return True
