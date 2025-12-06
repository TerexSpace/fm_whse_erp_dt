import pandas as pd
import numpy as np
from scipy import stats
import os

def perform_analysis():
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    raw_data_path = os.path.join(results_dir, 'table_1_raw.csv')
    
    if not os.path.exists(raw_data_path):
        print(f"Error: {raw_data_path} not found.")
        return

    df = pd.read_csv(raw_data_path)
    
    # Metrics to analyze
    metrics = ['inventory_discrepancy_rate', 'order_fulfillment_time', 'consensus_latency', 'privacy_preservation']
    
    print("Statistical Analysis Report")
    print("===========================")
    
    # Compare FM-ERP vs Baseline Centralized (for IDR and OFT)
    print("\nComparison: FM-ERP vs Baseline Centralized")
    fm_erp_data = df[df['System'] == 'FM-ERP']
    centralized_data = df[df['System'] == 'Baseline-Centralized']
    
    for metric in ['IDR', 'OFT']:
        stat, p_value = stats.ttest_ind(fm_erp_data[metric], centralized_data[metric])
        print(f"Metric: {metric}")
        print(f"  FM-ERP Mean: {fm_erp_data[metric].mean():.4f}")
        print(f"  Centralized Mean: {centralized_data[metric].mean():.4f}")
        print(f"  t-statistic: {stat:.4f}, p-value: {p_value:.4e}")
        if p_value < 0.01:
            print("  Result: Statistically Significant (p < 0.01)")
        else:
            print("  Result: Not Significant")

    # Compare FM-ERP vs Baseline Blockchain (for Consensus Latency)
    print("\nComparison: FM-ERP vs Baseline Blockchain")
    blockchain_data = df[df['System'] == 'Baseline-Blockchain']
    
    metric = 'CL'
    stat, p_value = stats.ttest_ind(fm_erp_data[metric], blockchain_data[metric])
    print(f"Metric: {metric}")
    print(f"  FM-ERP Mean: {fm_erp_data[metric].mean():.4f}")
    print(f"  Blockchain Mean: {blockchain_data[metric].mean():.4f}")
    print(f"  t-statistic: {stat:.4f}, p-value: {p_value:.4e}")
    if p_value < 0.01:
        print("  Result: Statistically Significant (p < 0.01)")
    else:
        print("  Result: Not Significant")

    # Compare FM-ERP vs Baseline FL (for Privacy)
    print("\nComparison: FM-ERP vs Baseline FL")
    fl_data = df[df['System'] == 'Baseline-FL']
    
    metric = 'PP'
    stat, p_value = stats.ttest_ind(fm_erp_data[metric], fl_data[metric])
    print(f"Metric: {metric}")
    print(f"  FM-ERP Mean: {fm_erp_data[metric].mean():.4f}")
    print(f"  Baseline FL Mean: {fl_data[metric].mean():.4f}")
    print(f"  t-statistic: {stat:.4f}, p-value: {p_value:.4e}")
    if p_value < 0.01:
        print("  Result: Statistically Significant (p < 0.01)")
    else:
        print("  Result: Not Significant")

if __name__ == "__main__":
    perform_analysis()
