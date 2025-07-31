#!/usr/bin/env python3
"""
Système de surveillance du dossier back-end/data pour détecter les nouveaux JSON
et lancer automatiquement l'extraction des personnages
"""

import os
import json
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FandomRequestHandler(FileSystemEventHandler):
    """Gestionnaire d'événements pour les nouveaux fichiers JSON"""
    
    def __init__(self):
        self.processed_files = set()
        
    def on_created(self, event):
        """Appelé quand un nouveau fichier est créé"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        
        # Vérifier que c'est un fichier JSON
        if not file_path.endswith('.json'):
            return
            
        # Éviter de traiter le même fichier plusieurs fois
        if file_path in self.processed_files:
            return
            
        print(f"🔍 Nouveau fichier détecté: {file_path}")
        
        # Attendre un peu pour s'assurer que le fichier est complètement écrit
        time.sleep(2)
        
        try:
            self.process_fandom_request(file_path)
            self.processed_files.add(file_path)
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file_path}: {e}")
    
    def process_fandom_request(self, file_path):
        """Traite une demande d'extraction de fandom"""
        print(f"📖 Lecture du fichier: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Vérifier la structure
            if 'url' not in data:
                print(f"❌ Pas d'URL trouvée dans {file_path}")
                return
                
            fandom_url = data['url']
            print(f"🎯 URL Fandom détectée: {fandom_url}")
            
            # Extraire le nom du fandom depuis l'URL
            fandom_name = self.extract_fandom_name(fandom_url)
            print(f"📛 Nom du fandom: {fandom_name}")
            
            # Lancer l'extraction
            self.launch_character_extraction(fandom_url, fandom_name, file_path)
            
        except json.JSONDecodeError:
            print(f"❌ Fichier JSON invalide: {file_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la lecture: {e}")
    
    def extract_fandom_name(self, url):
        """Extrait le nom du fandom depuis l'URL"""
        try:
            # Exemple: https://marvel.fandom.com/wiki/Marvel_Database -> marvel
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.split('.')[0]
        except:
            return "unknown_fandom"
    
    def launch_character_extraction(self, fandom_url, fandom_name, request_file):
        """Lance l'extraction des personnages pour un fandom"""
        print(f"🚀 Lancement de l'extraction pour {fandom_name}")
        
        # Créer un fichier temporaire avec la demande
        temp_request = {
            "fandom_name": fandom_name,
            "fandom_url": fandom_url,
            "request_file": request_file,
            "status": "processing"
        }
        
        temp_file = f"temp_request_{fandom_name}.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(temp_request, f, indent=2)
        
        try:
            # Lancer le spider d'extraction
            cmd = [
                'scrapy', 'crawl', 'single_fandom_extractor',
                '-a', f'fandom_url={fandom_url}',
                '-a', f'fandom_name={fandom_name}',
                '-a', f'request_file={request_file}',
                '-L', 'INFO'
            ]
            
            print(f"🔧 Commande: {' '.join(cmd)}")
            
            # Lancer en arrière-plan
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"✅ Extraction lancée pour {fandom_name} (PID: {process.pid})")
            
        except Exception as e:
            print(f"❌ Erreur lors du lancement: {e}")
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file):
                os.remove(temp_file)

def start_monitoring():
    """Démarre la surveillance du dossier back-end/data"""
    
    # Chemin vers le dossier à surveiller
    back_end_data_path = "../back-end/data"
    
    if not os.path.exists(back_end_data_path):
        print(f"❌ Dossier {back_end_data_path} non trouvé")
        print("Création du dossier pour les tests...")
        os.makedirs(back_end_data_path, exist_ok=True)
    
    print(f"👀 Surveillance du dossier: {os.path.abspath(back_end_data_path)}")
    print("🔄 En attente de nouveaux fichiers JSON...")
    print("💡 Pour tester, créez un fichier JSON avec: {\"url\": \"https://fandom_url\"}")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")
    
    # Créer l'observateur
    event_handler = FandomRequestHandler()
    observer = Observer()
    observer.schedule(event_handler, back_end_data_path, recursive=False)
    
    # Démarrer la surveillance
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de la surveillance...")
        observer.stop()
    
    observer.join()
    print("✅ Surveillance arrêtée")

if __name__ == "__main__":
    start_monitoring()