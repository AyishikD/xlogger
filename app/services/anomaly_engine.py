from typing import List, Dict, Any, Optional
import numpy as np
from pydantic import BaseModel

class AnomalyResult(BaseModel):
    anomaly_type: str
    severity: str
    confidence: float
    affected_metrics: List[str]
    description: str

class AnomalyEngine:
    def __init__(self, z_threshold: float = 3.0):
        self.z_threshold = z_threshold

    def detect_zscore_anomalies(
        self, 
        current_value: float, 
        history: List[float]
    ) -> Optional[float]:
        """
        Detect anomaly using Z-score.
        Returns the z-score if it exceeds threshold, else None.
        """
        if len(history) < 5:
            return None
            
        mean = np.mean(history)
        std = np.std(history)
        
        if std == 0:
            return None
            
        z_score = abs(current_value - mean) / std
        return z_score if z_score > self.z_threshold else None

    def detect_trend_break(
        self, 
        history: List[float], 
        window_size: int = 5
    ) -> Optional[str]:
        """
        Detect sudden breaks in metric trends.
        """
        if len(history) < window_size * 2:
            return None
            
        recent = history[-window_size:]
        previous = history[-window_size*2:-window_size]
        
        recent_slope = np.polyfit(range(window_size), recent, 1)[0]
        prev_slope = np.polyfit(range(window_size), previous, 1)[0]
        
        # Detect sign flip or significant slope change
        if np.sign(recent_slope) != np.sign(prev_slope) and abs(recent_slope - prev_slope) > 0.1:
            return "trend_reversal"
            
        if abs(recent_slope) > abs(prev_slope) * 5:
            return "acceleration_spike"
            
        return None

    def detect_divergence(self, history: List[float]) -> Optional[str]:
        """Detect if the metric is diverging from its baseline."""
        if len(history) < 10:
            return None
        
        baseline = np.mean(history[:5])
        current = history[-1]
        
        if baseline > 0 and current > baseline * 10:
            return "divergence_risk"
        return None

    def analyze_metrics(self, metric_data: Dict[str, List[float]]) -> List[AnomalyResult]:
        anomalies = []
        for metric, values in metric_data.items():
            if not values:
                continue
                
            current = values[-1]
            history = values[:-1]
            
            # 1. Z-Score Check
            z = self.detect_zscore_anomalies(current, history)
            if z:
                anomalies.append(AnomalyResult(
                    anomaly_type="statistical_outlier",
                    severity="critical" if z > 10 else "high" if z > 5 else "medium",
                    confidence=min(1.0, z / 15.0),
                    affected_metrics=[metric],
                    description=f"Metric {metric} deviated significantly from history (Z={round(z, 2)})"
                ))
            
            # 2. Trend Break Check
            break_type = self.detect_trend_break(values)
            if break_type:
                anomalies.append(AnomalyResult(
                    anomaly_type=break_type,
                    severity="medium",
                    confidence=0.7,
                    affected_metrics=[metric],
                    description=f"Trend break detected in {metric}: {break_type}"
                ))

            # 3. Divergence Check
            if metric in ["loss", "cost", "error"]:
                div = self.detect_divergence(values)
                if div:
                    anomalies.append(AnomalyResult(
                        anomaly_type=div,
                        severity="critical",
                        confidence=0.9,
                        affected_metrics=[metric],
                        description=f"Critical {div} detected in {metric}. Baseline exceeded by 10x."
                    ))
                
        return anomalies

    def get_predictions(self, metric_data: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Generate forward-looking risks/predictions based on current data."""
        predictions = []
        for metric, values in metric_data.items():
            if len(values) < 5: continue
            
            slope = np.polyfit(range(len(values)), values, 1)[0]
            if metric == "loss" and slope > 0:
                predictions.append({
                    "title": "Divergence Risk",
                    "confidence": min(0.95, slope * 10),
                    "status": "Critical" if slope > 0.1 else "Medium"
                })
            elif metric == "memory_usage" and slope > 0.01:
                predictions.append({
                    "title": "Potential Memory Leak",
                    "confidence": min(0.8, slope * 100),
                    "status": "Low"
                })
        return predictions

anomaly_engine = AnomalyEngine()
