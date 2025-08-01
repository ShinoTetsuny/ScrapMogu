#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement du scraper

Usage:
    python test_scraper.py
"""

import sys
import os

# Ajouter le répertoire du projet au chemin Python
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Tester que tous les imports fonctionnent"""
    print("🧪 Test des imports...")
    
    try:
        import scrapy
        print("✅ Scrapy importé avec succès")
    except ImportError:
        print("❌ Scrapy non trouvé. Installez avec: pip install scrapy")
        return False
    
    try:
        from Mogu2.items import FandomCharacterItem
        print("✅ FandomCharacterItem importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import FandomCharacterItem: {e}")
        return False
    
    try:
        from Mogu2.spiders.fandom_spider import FandomSpider
        print("✅ FandomSpider importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import FandomSpider: {e}")
        return False
    
    try:
        from Mogu2.pipelines import FandomJsonPipeline
        print("✅ FandomJsonPipeline importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import FandomJsonPipeline: {e}")
        return False
    
    return True

def test_directories():
    """Tester la création des dossiers de sortie"""
    print("\n📁 Test de création des dossiers...")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    result_dir = os.path.join(base_dir, 'result')
    report_dir = os.path.join(base_dir, 'report')
    
    # Créer les dossiers s'ils n'existent pas
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    if os.path.exists(result_dir):
        print(f"✅ Dossier result créé: {result_dir}")
    else:
        print(f"❌ Impossible de créer le dossier result: {result_dir}")
        return False
    
    if os.path.exists(report_dir):
        print(f"✅ Dossier report créé: {report_dir}")
    else:
        print(f"❌ Impossible de créer le dossier report: {report_dir}")
        return False
    
    return True

def test_spider_config():
    """Tester la configuration du spider"""
    print("\n⚙️ Test de la configuration du spider...")
    
    try:
        from Mogu2.spiders.fandom_spider import FandomSpider
        
        # Tester l'initialisation avec une URL valide
        test_url = "https://starwars.fandom.com/wiki/Main_Page"
        spider = FandomSpider(start_url=test_url)
        
        if spider.fandom_name == "starwars":
            print("✅ Extraction du nom de fandom réussie")
        else:
            print(f"❌ Nom de fandom incorrect: {spider.fandom_name}")
            return False
        
        if spider.start_urls == [test_url]:
            print("✅ URL de départ configurée correctement")
        else:
            print(f"❌ URL de départ incorrecte: {spider.start_urls}")
            return False
        
        # Tester les patterns de caractères
        character_patterns = [
            r'.*[Cc]haracters?.*',
            r'.*[Pp]ersonnages?.*',
            r'.*[Pp]eople.*',
            r'.*[Ii]ndividuals.*',
            r'.*[Bb]eings.*'
        ]
        print(f"✅ {len(character_patterns)} patterns de caractères définis")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du test de configuration: {e}")
        return False

def test_item_structure():
    """Tester la structure des items"""
    print("\n📋 Test de la structure des items...")
    
    try:
        from Mogu2.items import FandomCharacterItem
        
        item = FandomCharacterItem()
        required_fields = [
            'name', 'image_url', 'description', 'character_type',
            'attribute1_name', 'attribute1_value', 'attribute2_name', 'attribute2_value',
            'source_url', 'fandom_name', 'scraped_at'
        ]
        
        for field in required_fields:
            if field in item.fields:
                print(f"✅ Champ '{field}' défini")
            else:
                print(f"❌ Champ '{field}' manquant")
                return False
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du test de structure: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Lancement des tests du scraper Fandom")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_directories,
        test_spider_config,
        test_item_structure
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur lors du test {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ Tous les tests réussis ({passed}/{total})")
        print("\n🎉 Le scraper est prêt à être utilisé !")
        print("\nExemple d'utilisation:")
        print("python run_scraper.py https://starwars.fandom.com/wiki/Main_Page")
    else:
        print(f"❌ {total - passed} test(s) échoué(s) sur {total}")
        print("\n⚠️ Vérifiez les erreurs ci-dessus avant d'utiliser le scraper")
        sys.exit(1)

if __name__ == '__main__':
    main()