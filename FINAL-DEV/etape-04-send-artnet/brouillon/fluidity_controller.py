#!/usr/bin/env python3
"""
🎛️ CONFIGURATEUR FPS & BENCHMARK DE PERFORMANCE 🎛️

Outil pour tester et optimiser la fluidité en temps réel
"""

import time
import threading
import sys
import os

# Import du pipeline optimisé
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-04-send-artnet')
from ehub_pipeline_optimized_fluidity import EHubFluidPipeline

class FluidityBenchmark:
    """
    🏃 Benchmark et test de fluidité en temps réel
    """
    
    def __init__(self):
        self.pipeline = None
        self.running = False
        self.test_duration = 10  # secondes par test
        
    def test_fps_range(self, fps_list: list):
        """Teste une gamme de FPS et mesure les performances"""
        print("🎯 BENCHMARK FPS - Test de fluidité")
        print("=" * 50)
        
        results = {}
        
        for fps in fps_list:
            print(f"\n🔥 Test à {fps} FPS...")
            
            # Créer pipeline avec FPS spécifique
            pipeline = EHubFluidPipeline(target_fps=fps)
            
            if not pipeline.initialize():
                print(f"❌ Échec init pour {fps} FPS")
                continue
            
            # Test pendant duration secondes
            start_time = time.time()
            test_time = 0
            frame_count = 0
            
            try:
                while test_time < self.test_duration:
                    # Simuler réception de données
                    data = pipeline.dmx_pipeline.udp_receiver.receive_packet()
                    if data:
                        dmx_universes = pipeline.dmx_pipeline.process_ehub_packet(data)
                        if dmx_universes:
                            success = pipeline.optimized_sender.send_dmx_universes_optimized(dmx_universes)
                            if success:
                                frame_count += 1
                    
                    test_time = time.time() - start_time
                
            except KeyboardInterrupt:
                break
            
            # Récupérer les stats
            stats = pipeline.get_performance_report()
            results[fps] = {
                'frames_processed': frame_count,
                'actual_fps': stats['artnet_stats']['fps_actual'],
                'cache_hits': stats['artnet_stats']['cache_hits'],
                'cache_misses': stats['artnet_stats']['cache_misses'],
                'dropped_frames': stats['artnet_stats']['dropped_frames'],
                'avg_send_time': stats['artnet_stats']['send_time_avg'] * 1000  # en ms
            }
            
            pipeline.close()
            
            # Afficher résultats immédiats
            self._print_fps_result(fps, results[fps])
        
        # Résumé final
        self._print_benchmark_summary(results)
        return results
    
    def _print_fps_result(self, fps: int, result: dict):
        """Affiche le résultat d'un test FPS"""
        print(f"  📊 {fps} FPS:")
        print(f"    - FPS réel: {result['actual_fps']:.1f}")
        print(f"    - Frames traitées: {result['frames_processed']}")
        print(f"    - Temps envoi moyen: {result['avg_send_time']:.2f}ms")
        print(f"    - Frames droppées: {result['dropped_frames']}")
        
        # Cache performance
        total_cache = result['cache_hits'] + result['cache_misses']
        if total_cache > 0:
            cache_ratio = result['cache_hits'] / total_cache * 100
            print(f"    - Cache hit: {cache_ratio:.1f}%")
    
    def _print_benchmark_summary(self, results: dict):
        """Affiche le résumé des benchmarks"""
        print("\n" + "=" * 60)
        print("📈 RÉSUMÉ DES PERFORMANCES")
        print("=" * 60)
        
        # Trouver le meilleur FPS
        best_fps = None
        best_efficiency = 0
        
        for fps, stats in results.items():
            # Efficacité = (FPS réel / FPS cible) avec bonus pour faible latence
            efficiency = (stats['actual_fps'] / fps) * 100
            latency_bonus = max(0, 50 - stats['avg_send_time']) / 50 * 10  # Bonus pour latence < 50ms
            total_efficiency = efficiency + latency_bonus
            
            if total_efficiency > best_efficiency and stats['dropped_frames'] == 0:
                best_efficiency = total_efficiency
                best_fps = fps
            
            print(f"{fps:3d} FPS -> {stats['actual_fps']:5.1f} réel | "
                  f"{stats['avg_send_time']:5.2f}ms latence | "
                  f"{stats['dropped_frames']:3d} drops | "
                  f"Efficacité: {total_efficiency:.1f}%")
        
        if best_fps:
            print(f"\n🏆 OPTIMAL: {best_fps} FPS (efficacité: {best_efficiency:.1f}%)")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS:")
        if any(r['dropped_frames'] > 0 for r in results.values()):
            print("  ⚠️  Frames droppées détectées -> Réduire le FPS cible")
        
        high_latency = [fps for fps, r in results.items() if r['avg_send_time'] > 16.67]
        if high_latency:
            print(f"  ⚠️  Latence élevée à {high_latency} FPS -> Optimiser réseau")
        
        low_cache = [fps for fps, r in results.items() if r['cache_hits'] + r['cache_misses'] > 0 and 
                     r['cache_hits'] / (r['cache_hits'] + r['cache_misses']) < 0.5]
        if low_cache:
            print(f"  💾 Cache faible à {low_cache} FPS -> Ajuster cache timeout")

def interactive_fps_control():
    """Mode interactif pour changer le FPS en temps réel"""
    print("🎛️  MODE INTERACTIF - Contrôle FPS temps réel")
    print("=" * 50)
    
    pipeline = EHubFluidPipeline(target_fps=60)
    
    if not pipeline.initialize():
        print("❌ Échec initialisation")
        return
    
    print("🎮 COMMANDES:")
    print("  1-9: Changer FPS (1=10fps, 2=20fps, ..., 9=90fps)")
    print("  0: 100 FPS")
    print("  s: Statistiques")
    print("  q: Quitter")
    print("  Ctrl+C: Arrêt d'urgence")
    
    # Thread pour le pipeline
    def pipeline_runner():
        try:
            pipeline.run_ultra_fluid()
        except:
            pass
    
    pipeline_thread = threading.Thread(target=pipeline_runner, daemon=True)
    pipeline_thread.start()
    
    # Boucle de contrôle interactif
    try:
        while True:
            try:
                cmd = input("\n🎛️  FPS Control > ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == 's':
                    stats = pipeline.get_performance_report()
                    print(f"\n📊 STATS TEMPS RÉEL:")
                    print(f"  FPS cible: {stats['target_fps']}")
                    print(f"  FPS réel: {stats['artnet_stats']['fps_actual']:.1f}")
                    print(f"  Frames envoyées: {stats['artnet_stats']['frames_sent']}")
                    print(f"  Latence moyenne: {stats['artnet_stats']['send_time_avg']*1000:.2f}ms")
                    print(f"  Frames droppées: {stats['artnet_stats']['dropped_frames']}")
                elif cmd.isdigit():
                    fps_map = {'1': 10, '2': 20, '3': 30, '4': 40, '5': 50, 
                              '6': 60, '7': 70, '8': 80, '9': 90, '0': 100}
                    if cmd in fps_map:
                        new_fps = fps_map[cmd]
                        pipeline.set_fps(new_fps)
                        print(f"🎯 FPS modifié: {new_fps}")
                else:
                    print("❌ Commande inconnue")
                    
            except EOFError:
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    finally:
        pipeline.close()

def main():
    """Menu principal pour les tests de fluidité"""
    print("🔥 OPTIMISEUR DE FLUIDITÉ LED 🔥")
    print("=" * 40)
    print("1. Benchmark automatique FPS")
    print("2. Contrôle interactif FPS")
    print("3. Test de charge réseau")
    print("4. Quitter")
    
    choice = input("\nChoix > ").strip()
    
    if choice == '1':
        print("\n🏁 BENCHMARK AUTOMATIQUE")
        benchmark = FluidityBenchmark()
        fps_to_test = [30, 40, 50, 60, 75, 90, 120]
        benchmark.test_fps_range(fps_to_test)
        
    elif choice == '2':
        interactive_fps_control()
        
    elif choice == '3':
        print("🌐 Test de charge réseau - À implémenter")
        # TODO: Test de saturation réseau
        
    elif choice == '4':
        print("👋 Au revoir!")
        
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    main()
