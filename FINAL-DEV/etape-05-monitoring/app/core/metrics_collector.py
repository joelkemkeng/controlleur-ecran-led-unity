"""
📊 Metrics Collector - Collecte et traitement des métriques en temps réel
Calcule les tendances, moyennes et statistiques pour l'UI
"""

import time
from collections import deque
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MetricPoint:
    """Point de métrique avec timestamp"""
    timestamp: datetime
    value: float
    
@dataclass
class MetricTrend:
    """Tendance d'une métrique"""
    current_value: float
    previous_value: float
    change_percent: float
    trend_direction: str  # "up", "down", "stable"
    trend_symbol: str     # "↗", "↘", "●"

class MetricsCollector:
    """
    📊 Collecteur de métriques temps réel avec calculs de tendances
    """
    
    def __init__(self, history_size: int = 300):  # 5 minutes à 1Hz
        self.history_size = history_size
        
        # Historiques des métriques (deque circulaire)
        self.metrics_history: Dict[str, deque] = {
            "packets_per_second": deque(maxlen=history_size),
            "entities_processed": deque(maxlen=history_size),
            "latency_ms": deque(maxlen=history_size),
            "bytes_per_second": deque(maxlen=history_size),
            "errors_count": deque(maxlen=history_size),
            "controllers_active": deque(maxlen=history_size)
        }
        
        # Cache des dernières valeurs pour calcul tendances
        self.last_values: Dict[str, float] = {}
        
        # Seuils pour déterminer les tendances
        self.trend_thresholds = {
            "stable_percent": 5.0,  # ±5% = stable
            "significant_change": 10.0  # ±10% = changement significatif
        }
        
        print("📊 [MetricsCollector] Initialisé")
    
    def add_metric_point(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """
        📈 Ajoute un point de métrique à l'historique
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        point = MetricPoint(timestamp, value)
        
        if metric_name in self.metrics_history:
            self.metrics_history[metric_name].append(point)
        else:
            # Nouvelle métrique
            self.metrics_history[metric_name] = deque(maxlen=self.history_size)
            self.metrics_history[metric_name].append(point)
    
    def get_metric_trend(self, metric_name: str, lookback_seconds: int = 30) -> Optional[MetricTrend]:
        """
        📊 Calcule la tendance d'une métrique sur une période
        """
        if metric_name not in self.metrics_history:
            return None
        
        history = self.metrics_history[metric_name]
        if len(history) < 2:
            return None
        
        # Obtenir les valeurs actuelles et passées
        current_point = history[-1]
        current_value = current_point.value
        
        # Trouver le point de référence (il y a X secondes)
        reference_time = current_point.timestamp - timedelta(seconds=lookback_seconds)
        reference_value = self._find_closest_value(history, reference_time)
        
        if reference_value is None:
            reference_value = history[0].value  # Utiliser la première valeur
        
        # Calculer le changement
        if reference_value == 0:
            change_percent = 0.0
        else:
            change_percent = ((current_value - reference_value) / reference_value) * 100
        
        # Déterminer la direction de la tendance
        trend_direction, trend_symbol = self._calculate_trend_direction(change_percent)
        
        return MetricTrend(
            current_value=current_value,
            previous_value=reference_value,
            change_percent=change_percent,
            trend_direction=trend_direction,
            trend_symbol=trend_symbol
        )
    
    def _find_closest_value(self, history: deque, target_time: datetime) -> Optional[float]:
        """Trouve la valeur la plus proche d'un timestamp donné"""
        if not history:
            return None
        
        closest_point = None
        min_diff = float('inf')
        
        for point in history:
            diff = abs((point.timestamp - target_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest_point = point
        
        return closest_point.value if closest_point else None
    
    def _calculate_trend_direction(self, change_percent: float) -> Tuple[str, str]:
        """Calcule la direction et le symbole de tendance"""
        threshold = self.trend_thresholds["stable_percent"]
        
        if abs(change_percent) <= threshold:
            return "stable", "●"
        elif change_percent > threshold:
            return "up", "↗"
        else:
            return "down", "↘"
    
    def get_metric_average(self, metric_name: str, lookback_seconds: int = 60) -> Optional[float]:
        """
        📊 Calcule la moyenne d'une métrique sur une période
        """
        if metric_name not in self.metrics_history:
            return None
        
        history = self.metrics_history[metric_name]
        if not history:
            return None
        
        # Filtrer les points dans la période
        cutoff_time = datetime.now() - timedelta(seconds=lookback_seconds)
        recent_points = [p for p in history if p.timestamp >= cutoff_time]
        
        if not recent_points:
            return None
        
        # Calculer la moyenne
        total = sum(p.value for p in recent_points)
        return total / len(recent_points)
    
    def get_metric_min_max(self, metric_name: str, lookback_seconds: int = 300) -> Optional[Tuple[float, float]]:
        """
        📊 Retourne min et max d'une métrique sur une période
        """
        if metric_name not in self.metrics_history:
            return None
        
        history = self.metrics_history[metric_name]
        if not history:
            return None
        
        # Filtrer les points dans la période
        cutoff_time = datetime.now() - timedelta(seconds=lookback_seconds)
        recent_points = [p for p in history if p.timestamp >= cutoff_time]
        
        if not recent_points:
            return None
        
        values = [p.value for p in recent_points]
        return min(values), max(values)
    
    def get_chart_data(self, metric_name: str, max_points: int = 60) -> List[Tuple[datetime, float]]:
        """
        📈 Retourne les données pour affichage graphique
        """
        if metric_name not in self.metrics_history:
            return []
        
        history = self.metrics_history[metric_name]
        if not history:
            return []
        
        # Prendre les N derniers points
        recent_points = list(history)[-max_points:]
        
        return [(p.timestamp, p.value) for p in recent_points]
    
    def get_all_current_metrics(self) -> Dict[str, float]:
        """
        📊 Retourne toutes les métriques actuelles
        """
        current_metrics = {}
        
        for metric_name, history in self.metrics_history.items():
            if history:
                current_metrics[metric_name] = history[-1].value
            else:
                current_metrics[metric_name] = 0.0
        
        return current_metrics
    
    def format_trend_text(self, trend: MetricTrend) -> str:
        """
        📊 Formate le texte de tendance pour l'affichage
        """
        if trend.trend_direction == "stable":
            return f"{trend.trend_symbol} Stable"
        else:
            sign = "+" if trend.change_percent > 0 else ""
            return f"{trend.trend_symbol} {sign}{trend.change_percent:.1f}%"
    
    def clear_metrics(self):
        """
        🗑️ Vide toutes les métriques
        """
        for history in self.metrics_history.values():
            history.clear()
        self.last_values.clear()
        print("🗑️ [MetricsCollector] Métriques effacées")
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        📊 Retourne un résumé statistique complet
        """
        summary = {}
        
        for metric_name in self.metrics_history:
            history = self.metrics_history[metric_name]
            if not history:
                continue
            
            # Valeurs de base
            current = history[-1].value if history else 0
            avg_1min = self.get_metric_average(metric_name, 60) or 0
            avg_5min = self.get_metric_average(metric_name, 300) or 0
            
            # Min/Max dernière minute
            min_max = self.get_metric_min_max(metric_name, 60)
            min_val, max_val = min_max if min_max else (0, 0)
            
            # Tendance
            trend = self.get_metric_trend(metric_name, 30)
            
            summary[metric_name] = {
                "current": current,
                "avg_1min": avg_1min,
                "avg_5min": avg_5min,
                "min_1min": min_val,
                "max_1min": max_val,
                "trend": self.format_trend_text(trend) if trend else "● N/A",
                "points_count": len(history)
            }
        
        return summary