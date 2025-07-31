#!/usr/bin/env python3
"""
Script pour surveiller les progrès du scraping
"""

import os
import time
import json
from pathlib import Path

def monitor_progress():
    """Surveille les fichiers de rapport pour afficher les progrès"""
    
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print("❌ Dossier reports non trouvé")
        return
    
    print("🔍 Surveillance des progrès du scraping...")
    print("Appuyez sur Ctrl+C pour arrêter la surveillance")
    print("-" * 50)
    
    last_count = 0
    
    try:
        while True:
            # Chercher le fichier de rapport le plus récent
            json_files = list(reports_dir.glob("fandom_analysis_*.json"))
            
            if json_files:
                latest_report = max(json_files, key=os.path.getctime)
                
                try:
                    with open(latest_report, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    stats = data.get('stats', {})
                    current_count = stats.get('total_fandoms', 0)
                    
                    if current_count > last_count:
                        print(f"📈 Progrès: {current_count}/218 fandoms analysés")
                        print(f"   ✅ Succès: {stats.get('successful_fandoms', 0)}")
                        print(f"   🎯 Avec personnages: {stats.get('fandoms_with_characters', 0)}")
                        print(f"   👥 Total personnages: {stats.get('total_characters_found', 0)}")
                        print(f"   ❌ Erreurs: {stats.get('errors', 0)}")
                        
                        if stats.get('successful_fandoms', 0) > 0:
                            success_rate = (stats.get('fandoms_with_characters', 0) / stats.get('successful_fandoms', 1)) * 100
                            print(f"   📊 Taux de détection: {success_rate:.1f}%")
                        
                        print("-" * 50)
                        last_count = current_count
                        
                        # Si terminé
                        if current_count >= 218:
                            print("🎉 Analyse complète terminée !")
                            break
                
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
            
            time.sleep(10)  # Vérifier toutes les 10 secondes
            
    except KeyboardInterrupt:
        print("\n👋 Surveillance interrompue par l'utilisateur")

if __name__ == "__main__":
    monitor_progress()