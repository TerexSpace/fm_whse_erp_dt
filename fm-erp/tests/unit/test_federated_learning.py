import pytest
import torch
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
from services.federated_learning.models.demand_predictor import LSTMDemandForecaster
from services.federated_learning.fl_client import FMERPFederatedClient
from services.federated_learning.strategies.fedavg_weighted import ByzantineRobustStrategy, FedAvgAggregator, KrumSelector, GaussianDPMechanism

# Mock data for testing
def create_dummy_data(num_samples=100, seq_len=10, input_size=10):
    X = torch.randn(num_samples, seq_len, input_size)
    y = torch.randn(num_samples, 1)
    dataset = TensorDataset(X, y)
    return DataLoader(dataset, batch_size=10)

class TestFederatedLearning:
    
    def test_model_initialization(self):
        """Test LSTM model initialization and forward pass"""
        model = LSTMDemandForecaster(input_size=10, hidden_size=32)
        dummy_input = torch.randn(5, 10, 10) # Batch=5, Seq=10, Feat=10
        output = model(dummy_input)
        assert output.shape == (5, 1)

    def test_client_fit(self):
        """Test client training loop"""
        train_loader = create_dummy_data()
        val_loader = create_dummy_data()
        client = FMERPFederatedClient("client1", train_loader, val_loader)
        
        # Get initial parameters
        initial_params = client.get_parameters(config={})
        
        # Perform fit
        updated_params, num_examples, metrics = client.fit(initial_params, config={"local_epochs": 1})
        
        assert len(updated_params) == len(initial_params)
        assert num_examples == 100
        assert "gradient_hash" in metrics

    def test_gradient_hashing(self):
        """Test SHA-256 hashing is deterministic"""
        train_loader = create_dummy_data()
        val_loader = create_dummy_data()
        client = FMERPFederatedClient("client1", train_loader, val_loader)
        
        params = [np.array([1, 2, 3], dtype=np.float32)]
        hash1 = client.compute_gradient_hash(params)
        hash2 = client.compute_gradient_hash(params)
        
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64 # SHA-256 length

    def test_coordinate_wise_median(self):
        """Test median aggregation strategy"""
        strategy = ByzantineRobustStrategy()
        
        # Create 3 clients with simple weights
        # Client 1: [1, 1, 1]
        # Client 2: [2, 2, 2]
        # Client 3: [100, 100, 100] (Outlier)
        
        w1 = [np.array([1, 1, 1])]
        w2 = [np.array([2, 2, 2])]
        w3 = [np.array([100, 100, 100])]
        
        weights_list = [w1, w2, w3]
        
        aggregated = strategy.coordinate_wise_median(weights_list)
        
        # Median of 1, 2, 100 is 2
        expected = np.array([2, 2, 2])
        np.testing.assert_array_equal(aggregated[0], expected)

    def test_differential_privacy(self):
        """Test DP noise injection"""
        train_loader = create_dummy_data()
        val_loader = create_dummy_data()
        client = FMERPFederatedClient("client1", train_loader, val_loader)
        
        params = [np.zeros((10, 10))]
        noisy_params = client.add_differential_privacy(params, epsilon=0.1)
        
        assert not np.array_equal(params[0], noisy_params[0])
        assert params[0].shape == noisy_params[0].shape

    def test_fedavg_aggregation_correctness(self):
        """Test FedAvg produces correct weighted average"""
        # Create 3 mock gradients
        grad1 = np.array([1.0, 2.0, 3.0])
        grad2 = np.array([4.0, 5.0, 6.0])
        grad3 = np.array([7.0, 8.0, 9.0])
        
        gradients = [grad1, grad2, grad3]
        weights = [10, 20, 30]  # Data sizes
        
        # Expected: weighted average
        expected = (10*grad1 + 20*grad2 + 30*grad3) / 60
        
        # Actual: FedAvg aggregation
        aggregator = FedAvgAggregator()
        actual = aggregator.aggregate(gradients, weights)
        
        np.testing.assert_array_almost_equal(actual, expected)
        
    def test_byzantine_detection_krum(self):
        """Test Krum detects Byzantine gradients"""
        # 5 honest gradients (close together)
        honest_grads = [np.random.randn(10) + 5.0 for _ in range(5)]
        
        # 2 Byzantine gradients (outliers)
        byzantine_grads = [np.random.randn(10) + 100.0 for _ in range(2)]
        
        all_grads = honest_grads + byzantine_grads
        
        # Krum should select honest gradient
        krum_selector = KrumSelector(num_byzantine=2)
        selected = krum_selector.select(all_grads)
        
        # Verify selected gradient is from honest set
        min_distance = min(np.linalg.norm(selected - h) for h in honest_grads)
        assert min_distance < 1.0  # Selected is close to honest gradients
        
    @pytest.mark.parametrize("epsilon,delta", [(1.0, 1e-5), (0.1, 1e-3)])
    def test_differential_privacy_guarantees(self, epsilon, delta):
        """Test DP noise satisfies (ε,δ)-differential privacy"""
        gradient = np.random.randn(100)
        
        # Apply DP noise
        dp_mechanism = GaussianDPMechanism(epsilon=epsilon, delta=delta, sensitivity=1.0)
        noisy_gradient = dp_mechanism.add_noise(gradient)
        
        # Test: Noise magnitude proportional to 1/ε
        noise = noisy_gradient - gradient
        noise_std = np.std(noise)
        
        # Gaussian DP: σ = sensitivity * sqrt(2*ln(1.25/δ)) / ε
        expected_std = 1.0 * np.sqrt(2 * np.log(1.25/delta)) / epsilon
        
        assert abs(noise_std - expected_std) / expected_std < 0.1  # Within 10%
