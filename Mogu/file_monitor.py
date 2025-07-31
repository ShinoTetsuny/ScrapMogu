"""
Système de surveillance du fichier back-end/data/data.json pour lancer
automatiquement l'extraction des personnages.
"""

import os
import json
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from urllib.parse import urlparse

class DataJsonHandler(FileSystemEventHandler):
    """Gestionnaire d'événements pour le fichier data.json"""

    def __init__(self):
        self.processed_urls = set()
        # Charger les URLs déjà traitées au démarrage si nécessaire
        self.load_processed_urls()

    def on_modified(self, event):
        """Appelé quand un fichier est modifié"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.name == 'data.json':
            print(f"🔄 Fichier 'data.json' modifié. Vérification des nouvelles URLs...")
            time.sleep(1)  # Attendre que le fichier soit complètement écrit
            self.process_data_json(file_path)

    def process_data_json(self, file_path):
        """Traite le fichier data.json pour extraire les nouvelles URLs"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Rendre le script plus robuste: accepter un objet seul ou une liste d'objets
            if isinstance(data, dict):
                requests = [data]
            elif isinstance(data, list):
                requests = data
            else:
                print(f"❌ Erreur: {file_path} doit contenir un objet JSON ou une liste d'objets.")
                return

            new_requests_found = 0
            for req in requests:
                if isinstance(req, dict) and 'url' in req and req['url'] not in self.processed_urls:
                    fandom_url = req['url']
                    print(f"🎯 Nouvelle URL détectée: {fandom_url}")
                    
                    self.processed_urls.add(fandom_url)
                    self.save_processed_urls() # Sauvegarder l'état
                    
                    fandom_name = self.extract_fandom_name(fandom_url)
                    self.launch_character_extraction(fandom_url, fandom_name)
                    new_requests_found += 1

            if new_requests_found > 0:
                 print(f"✅ {new_requests_found} nouvelle(s) demande(s) traitée(s).")
            else:
                print("✅ Aucune nouvelle URL à traiter dans data.json.")

        except json.JSONDecodeError:
            print(f"❌ Fichier JSON invalide: {file_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de {file_path}: {e}")

    def extract_fandom_name(self, url):
        """Extrait le nom du fandom depuis l'URL"""
        try:
            return urlparse(url).netloc.split('.')[0]
        except Exception as e:
            print(f"⚠️  Impossible d'extraire le nom du fandom de {url}: {e}")
            return f"unknown_fandom_{int(time.time())}"

    def launch_character_extraction(self, fandom_url, fandom_name):
        """Lance l'extraction des personnages pour un fandom"""
        print(f"🚀 Lancement de l'extraction pour '{fandom_name}'...")
        try:
            cmd = [
                'scrapy', 'crawl', 'single_fandom_extractor',
                '-a', f'fandom_url={fandom_url}',
                '-a', f'fandom_name={fandom_name}',
                '-L', 'INFO'
            ]
            
            # Lancer en arrière-plan pour ne pas bloquer le moniteur
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"✅ Extraction lancée pour {fandom_name} (PID: {process.pid})")

        except FileNotFoundError:
            print("❌ Erreur: Scrapy n'est pas trouvé. Assurez-vous qu'il est installé et dans le PATH.")
        except Exception as e:
            print(f"❌ Erreur lors du lancement de Scrapy: {e}")

    def load_processed_urls(self):
        """Charge les URLs déjà traitées depuis un fichier de cache."""
        try:
            if Path("processed_urls.json").exists():
                with open("processed_urls.json", "r") as f:
                    self.processed_urls = set(json.load(f))
                    print(f"📚 {len(self.processed_urls)} URLs déjà traitées chargées.")
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Impossible de charger les URLs traitées: {e}")

    def save_processed_urls(self):
        """Sauvegarde l'ensemble des URLs traitées."""
        try:
            with open("processed_urls.json", "w") as f:
                json.dump(list(self.processed_urls), f)
        except IOError as e:
            print(f"⚠️  Impossible de sauvegarder les URLs traitées: {e}")


def start_monitoring():
    """Démarre la surveillance du dossier back-end/data"""
    back_end_data_path = Path("../back-end/data")
    
    if not back_end_data_path.exists():
        print(f"📂 Création du dossier de surveillance: {back_end_data_path.resolve()}")
        back_end_data_path.mkdir(parents=True, exist_ok=True)
    
    # Créer un fichier data.json vide s'il n'existe pas
    data_json_path = back_end_data_path / "data.json"
    if not data_json_path.exists():
        print(f"📄 Création du fichier 'data.json' initial.")
        with open(data_json_path, 'w') as f:
            json.dump([], f)

    print(f"👀 Surveillance du fichier: {data_json_path.resolve()}")
    print("💡 Modifiez ce fichier pour lancer une extraction.")
    print("   Format attendu: [{\"url\": \"https://...\"}, {\"url\": \"https://...\"}]")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")
    
    event_handler = DataJsonHandler()
    observer = Observer()
    observer.schedule(event_handler, str(back_end_data_path), recursive=False)
    
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