#!/usr/bin/env python3
"""
Script de lancement pour le scraper Fandom universel

Usage:
    python run_scraper.py https://starwars.fandom.com/wiki/Main_Page
    python run_scraper.py https://pokemon.fandom.com/wiki/Pokemon_Wiki
"""

import sys
import os
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Ajouter le répertoire du projet au chemin Python
sys.path.insert(0, os.path.dirname(__file__))

from Mogu2.spiders.fandom_spider import FandomSpider


def main():
    parser = argparse.ArgumentParser(
        description='Scraper universel pour les wikis Fandom',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Scraper 10 personnages Star Wars (défaut)
  python run_scraper.py https://starwars.fandom.com/wiki/Main_Page
  
  # Scraper 20 personnages Pokemon  
  python run_scraper.py https://pokemon.fandom.com/wiki/Pokemon_Wiki --max-characters 20
  
  # Scraper 5 personnages Marvel rapidement
  python run_scraper.py https://marvel.fandom.com/wiki/Marvel_Database --max-characters 5 --delay 1
  
Les résultats seront sauvegardés dans:
  - result/[nom_fandom]/[nom_fandom]_characters_[timestamp].json
  - report/[nom_fandom]/rapport_[nom_fandom]_[timestamp].json
        """
    )
    
    parser.add_argument(
        'fandom_url',
        help='URL de la page principale du fandom à scraper'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Niveau de log (défaut: INFO)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Délai entre les requêtes en secondes (défaut: 2.0)'
    )
    
    parser.add_argument(
        '--max-characters',
        type=int,
        default=10,
        help='Nombre maximum de personnages à extraire (défaut: 10)'
    )
    
    args = parser.parse_args()
    
    # Valider l'URL
    if not args.fandom_url.startswith('http'):
        print("❌ Erreur: L'URL doit commencer par http:// ou https://")
        sys.exit(1)
    
    if 'fandom.com' not in args.fandom_url:
        print("❌ Erreur: L'URL doit pointer vers un site fandom.com")
        sys.exit(1)
    
    print(f"🚀 Démarrage du scraping de: {args.fandom_url}")
    print(f"📊 Niveau de log: {args.log_level}")
    print(f"⏱️  Délai entre requêtes: {args.delay}s")
    print(f"🎯 Limite de personnages: {args.max_characters}")
    print("─" * 60)
    
    # Configuration Scrapy
    settings = get_project_settings()
    settings.update({
        'LOG_LEVEL': args.log_level,
        'DOWNLOAD_DELAY': args.delay,
    })
    
    # Créer et lancer le processus de crawl
    process = CrawlerProcess(settings)
    process.crawl(FandomSpider, start_url=args.fandom_url, max_characters=args.max_characters)
    
    try:
        process.start()
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du scraping: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()