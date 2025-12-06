import flwr as fl
import torch
import numpy as np
from typing import List, Tuple, Dict
import hashlib
from collections import OrderedDict

from .models.demand_predictor import LSTMDemandForecaster

class FMERPFederatedClient(fl.client.NumPyClient):
    def __init__(self, client_id: str, train_loader, val_loader, blockchain_client=None):
        """
        Initialize client with private warehouse data
        
        Args:
            client_id: Unique identifier for the client
            train_loader: PyTorch DataLoader for training data
            val_loader: PyTorch DataLoader for validation data
            blockchain_client: Optional client to interact with blockchain
        """
        self.client_id = client_id
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.blockchain_client = blockchain_client
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = LSTMDemandForecaster().to(self.device)

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        """Return model parameters as a list of NumPy arrays"""
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: List[np.ndarray]):
        """Set model parameters from a list of NumPy arrays"""
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters: List[np.ndarray], config: Dict[str, str]) -> Tuple[List[np.ndarray], int, Dict]:
        """Train local model, return updated parameters + metrics"""
        self.set_parameters(parameters)
        
        # Hyperparameters from config
        epochs = int(config.get("local_epochs", 1))
        lr = float(config.get("learning_rate", 0.01))
        
        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        
        self.model.train()
        for _ in range(epochs):
            for images, labels in self.train_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
        updated_parameters = self.get_parameters(config={})
        
        # Compute gradient hash for blockchain verification
        gradient_hash = self.compute_gradient_hash(updated_parameters)
        
        # In a real implementation, we would submit this hash to the blockchain here
        # if self.blockchain_client:
        #     self.blockchain_client.submit_hash(self.client_id, gradient_hash)
            
        return updated_parameters, len(self.train_loader.dataset), {"gradient_hash": gradient_hash}

    def evaluate(self, parameters: List[np.ndarray], config: Dict[str, str]) -> Tuple[float, int, Dict]:
        """Evaluate global model on local validation set"""
        self.set_parameters(parameters)
        criterion = torch.nn.MSELoss()
        loss = 0.0
        steps = 0
        
        self.model.eval()
        with torch.no_grad():
            for images, labels in self.val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss += criterion(outputs, labels).item()
                steps += 1
                
        if steps == 0:
            return 0.0, 0, {}
            
        return loss / steps, len(self.val_loader.dataset), {}

    def compute_gradient_hash(self, parameters: List[np.ndarray]) -> str:
        """SHA-256 hash of parameters for blockchain verification"""
        hasher = hashlib.sha256()
        for param in parameters:
            hasher.update(param.tobytes())
        return hasher.hexdigest()

    def add_differential_privacy(self, parameters: List[np.ndarray], epsilon: float = 1.0) -> List[np.ndarray]:
        """Add Gaussian noise for differential privacy (optional)"""
        # Simplified DP implementation
        noisy_params = []
        for param in parameters:
            noise = np.random.normal(0, 1.0/epsilon, param.shape)
            noisy_params.append(param + noise)
        return noisy_params
