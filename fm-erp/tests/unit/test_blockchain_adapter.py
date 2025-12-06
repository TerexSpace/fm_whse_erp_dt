import pytest
from unittest.mock import Mock, patch
from blockchain.sdk.podq_consensus import PoDQConsensus

class TestPoDQConsensus:
    """Unit tests for Proof-of-Data-Quality consensus mechanism"""
    
    @pytest.fixture
    def podq_consensus(self):
        """Fixture: Initialize PoDQ consensus with 15 nodes"""
        return PoDQConsensus(
            num_nodes=15,
            quorum_size=8,
            initial_reputation=0.5
        )
        
    def test_validator_selection_probability(self, podq_consensus):
        """Test validator selection follows reputation-weighted distribution"""
        # Set up known reputations
        reputations = {f"node_{i}": 0.5 + 0.1*i for i in range(15)}
        podq_consensus.reputations = reputations
        
        # Sample 10,000 validator selections
        selections = [podq_consensus.select_validators() for _ in range(10000)]
        
        # Count selections per node
        selection_counts = {}
        for validator_set in selections:
            for node in validator_set:
                selection_counts[node] = selection_counts.get(node, 0) + 1
                
        # Test: Higher reputation nodes selected more frequently
        assert selection_counts["node_14"] > selection_counts["node_0"]
        
        # Test: Selection probability proportional to reputation (±20% tolerance)
        expected_prob = reputations["node_14"] / sum(reputations.values())
        actual_prob = selection_counts["node_14"] / (10000 * podq_consensus.quorum_size)
        assert abs(actual_prob - expected_prob) / expected_prob < 0.20
        
    def test_reputation_update_honest_behavior(self, podq_consensus):
        """Test reputation increases for honest nodes"""
        node_id = "node_1"
        initial_rep = podq_consensus.reputations[node_id]
        
        # Simulate successful validation
        podq_consensus.update_reputation(node_id, quality_score=1.0)
        
        final_rep = podq_consensus.reputations[node_id]
        assert final_rep > initial_rep
        
    def test_reputation_update_malicious_behavior(self, podq_consensus):
        """Test reputation decreases for malicious nodes"""
        node_id = "node_1"
        initial_rep = podq_consensus.reputations[node_id]
        
        # Simulate malicious behavior (detected)
        podq_consensus.handle_malicious_behavior(node_id)
        
        final_rep = podq_consensus.reputations[node_id]
        assert final_rep < initial_rep
        assert final_rep == initial_rep * 0.5  # 50% penalty
        
    def test_byzantine_tolerance(self, podq_consensus):
        """Test consensus tolerates f=(N-1)/3 Byzantine nodes"""
        # Byzantine tolerance: f = floor((15-1)/3) = 4
        # Quorum: Q = 8 requires majority to be honest
        
        # Set 4 nodes as malicious (maximum tolerable)
        malicious_nodes = [f"node_{i}" for i in range(4)]
        honest_nodes = [f"node_{i}" for i in range(4, 15)]
        
        # Simulate transaction validation
        validations = {node: (node in honest_nodes) for node in podq_consensus.nodes}
        
        consensus_result = podq_consensus.reach_consensus(validations)
        assert consensus_result == True  # Consensus achieved with honest majority
        
    def test_consensus_finality_time(self, podq_consensus):
        """Test consensus finality < 3 seconds (from JUCS manuscript)"""
        import time
        
        # Mock network latency
        with patch('time.sleep', return_value=None):  # Disable sleep for testing
            start = time.time()
            
            # Simulate validator selection + endorsement + smart contract execution
            validators = podq_consensus.select_validators()
            endorsements = [podq_consensus.collect_endorsement(v) for v in validators]
            result = podq_consensus.execute_smart_contract(endorsements)
            
            finality_time = time.time() - start
            
        # Real-world includes network latency (~100ms) + smart contract (~50ms)
        # In test environment without network, should be <100ms
        assert finality_time < 0.1  # 100ms in test environment
