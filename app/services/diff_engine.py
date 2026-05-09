from typing import List, Dict, Any, Optional
import uuid

class DiffEngine:
    def compare_configs(self, config_a: Dict[str, Any], config_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute structured diff between two experiment configurations.
        """
        changed_fields = []
        added_fields = []
        removed_fields = []

        all_keys = set(config_a.keys()) | set(config_b.keys())
        
        for key in all_keys:
            if key in config_a and key in config_b:
                if config_a[key] != config_b[key]:
                    changed_fields.append({
                        "field": key,
                        "old": config_a[key],
                        "new": config_b[key]
                    })
            elif key in config_a:
                removed_fields.append({"field": key, "value": config_a[key]})
            else:
                added_fields.append({"field": key, "value": config_b[key]})

        # Identify Risk Factors
        risk_factors = []
        critical_keys = ["learning_rate", "optimizer", "batch_size", "precision", "tokenizer"]
        
        for change in changed_fields:
            if change["field"] in critical_keys:
                risk_factors.append(f"Change in {change['field']} detected: {change['old']} -> {change['new']}")

        # Likely regression sources (heuristics)
        likely_sources = []
        if any(c["field"] == "learning_rate" for c in changed_fields):
            likely_sources.append("learning_rate_adjustment")
        if any(c["field"] == "tokenizer" for c in changed_fields):
            likely_sources.append("tokenizer_mismatch")

        return {
            "changed_fields": changed_fields,
            "added_fields": added_fields,
            "removed_fields": removed_fields,
            "risk_factors": risk_factors,
            "likely_regression_sources": likely_sources
        }

    async def compare_experiments(self, exp_a: Any, exp_b: Any) -> Dict[str, Any]:
        """
        Compare two experiments comprehensively (configs + results).
        """
        config_diff = self.compare_configs(
            exp_a.metadata_json.get("config", {}),
            exp_b.metadata_json.get("config", {})
        )
        
        # Compare metrics if available
        metrics_a = exp_a.metadata_json.get("final_metrics", {})
        metrics_b = exp_b.metadata_json.get("final_metrics", {})
        
        metric_changes = {}
        for m in set(metrics_a.keys()) & set(metrics_b.keys()):
            val_a = metrics_a[m]
            val_b = metrics_b[m]
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                delta = val_b - val_a
                percent = (delta / val_a * 100) if val_a != 0 else 0
                metric_changes[m] = {"delta": delta, "percent": round(percent, 2)}

        return {
            "config_diff": config_diff,
            "metric_changes": metric_changes,
            "outcome_comparison": "improved" if metric_changes.get("loss", {}).get("delta", 0) < 0 else "regressed"
        }

diff_engine = DiffEngine()
