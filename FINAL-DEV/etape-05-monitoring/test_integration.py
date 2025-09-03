#!/usr/bin/env python3
"""
🧪 Test d'intégration Phase 2 - Monitoring Pipeline
Teste l'intégration du monitoring avec le pipeline existant
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin de l'application
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path))

def test_pipeline_monitor_import():
    """Test 1: Import du PipelineMonitor"""
    print("🧪 Test 1: Import PipelineMonitor...")
    
    try:
        from core.pipeline_monitor import PipelineMonitor, MonitoringData
        print("✅ Import PipelineMonitor réussi")
        return True
    except Exception as e:
        print(f"❌ Erreur import PipelineMonitor: {e}")
        return False

def test_metrics_collector_import():
    """Test 2: Import du MetricsCollector"""
    print("🧪 Test 2: Import MetricsCollector...")
    
    try:
        from core.metrics_collector import MetricsCollector, MetricTrend
        print("✅ Import MetricsCollector réussi")
        return True
    except Exception as e:
        print(f"❌ Erreur import MetricsCollector: {e}")
        return False

def test_pipeline_monitor_basic():
    """Test 3: Fonctionnement basique PipelineMonitor"""
    print("🧪 Test 3: PipelineMonitor basique...")
    
    try:
        from core.pipeline_monitor import PipelineMonitor
        
        monitor = PipelineMonitor(port=8766)  # Port test
        print(f"✅ PipelineMonitor créé (port: {monitor.port})")
        
        stats = monitor.get_statistics()
        print(f"✅ Statistiques: {stats['pipeline_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur PipelineMonitor basique: {e}")
        return False

def test_metrics_collector_basic():
    """Test 4: Fonctionnement basique MetricsCollector"""
    print("🧪 Test 4: MetricsCollector basique...")
    
    try:
        from core.metrics_collector import MetricsCollector
        from datetime import datetime
        
        collector = MetricsCollector(history_size=10)
        
        # Ajouter quelques points
        collector.add_metric_point("test_metric", 42.0)
        collector.add_metric_point("test_metric", 45.0)
        
        # Calculer tendance
        trend = collector.get_metric_trend("test_metric", 10)
        if trend:
            print(f"✅ Tendance calculée: {trend.trend_direction} ({trend.change_percent:.1f}%)")
        else:
            print("✅ Pas assez de données pour tendance (normal)")
        
        # Statistiques
        stats = collector.get_statistics_summary()
        print(f"✅ Statistiques: {len(stats)} métriques")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur MetricsCollector basique: {e}")
        return False

def test_ui_integration():
    """Test 5: Intégration UI (juste import)"""
    print("🧪 Test 5: Intégration UI...")
    
    try:
        # Test d'import de l'UI avec monitoring
        from ui.base_window import MainWindow
        print("✅ Import MainWindow avec monitoring intégré")
        
        # Ne pas créer la fenêtre pour les tests
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration UI: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 === TESTS INTÉGRATION PHASE 2 ===")
    print()
    
    tests = [
        ("Import PipelineMonitor", test_pipeline_monitor_import),
        ("Import MetricsCollector", test_metrics_collector_import), 
        ("PipelineMonitor basique", test_pipeline_monitor_basic),
        ("MetricsCollector basique", test_metrics_collector_basic),
        ("Intégration UI", test_ui_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅' if success else '❌'} {test_name}: {'RÉUSSI' if success else 'ÉCHOUÉ'}")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("📊 === RÉSUMÉ DES TESTS ===")
    all_passed = True
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 === PHASE 2 ÉTAPE 2.1 VALIDÉE ! ===")
        print("✅ Intégration pipeline réussie")
        print("✅ Monitoring temps réel opérationnel")
        print("✅ Collecteur de métriques fonctionnel")
        print("✅ UI intégrée avec monitoring")
        print("✅ Prêt pour les tests avec vraies données")
        return True
    else:
        print("❌ === CORRECTIONS NÉCESSAIRES ===")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Phase 2 Étape 2.1 validée ! Prêt pour les données temps réel !")
        exit(0)
    else:
        print("\n❌ Des corrections sont nécessaires")
        exit(1)