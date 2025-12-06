import torch
import torch.nn as nn

class LSTMDemandForecaster(nn.Module):
    """LSTM-based demand forecasting model"""
    def __init__(self, input_size: int = 10, hidden_size: int = 64, 
                 num_layers: int = 2, dropout: float = 0.2):
        """
        Args:
            input_size: Number of input features (historical demand, seasonality, etc.)
            hidden_size: LSTM hidden state dimension
            num_layers: Number of stacked LSTM layers
            dropout: Dropout probability for regularization
        """
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, 1)  # Output: demand prediction
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor [batch_size, seq_length, input_size]
        Returns:
            predictions: [batch_size, 1]
        """
        lstm_out, _ = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1, :])  # Use last time step
        return predictions
