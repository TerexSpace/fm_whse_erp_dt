from typing import List, Dict
import numpy as np

class StatisticalAnalyzer:
    """Statistical analysis of experimental results"""
    
    def paired_t_test(self, fm_erp_results: List[float], 
                      baseline_results: List[float],
                      alpha: float = 0.01) -> Dict:
        """
        Paired t-test: H0: μ_FM-ERP = μ_baseline
        
        Args:
            fm_erp_results: List of metric values from FM-ERP (N=10 runs)
            baseline_results: List of metric values from baseline (N=10 runs)
            alpha: Significance level (0.01 for p<0.01)
            
        Returns:
            Dict with t-statistic, p-value, significant (bool)
        """
        try:
            from scipy import stats
            t_stat, p_value = stats.ttest_rel(fm_erp_results, baseline_results)
        except ImportError:
            # Fallback if scipy not installed
            t_stat, p_value = 0.0, 1.0
        
        return {
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < alpha,
            "effect_size": self._cohen_d(fm_erp_results, baseline_results)
        }
        
    def _cohen_d(self, group1: List[float], group2: List[float]) -> float:
        """Cohen's d effect size: (μ1 - μ2) / σ_pooled"""
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)
        
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))
        if pooled_std == 0:
            return 0.0
        d = (mean1 - mean2) / pooled_std
        return d
