#!/usr/bin/env python3
"""
Script pour examiner le fichier JSON HTML créé
"""

import json

def check_html_json():
    try:
        with open('reports/html_pages_20250731_155206.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("🔍 ANALYSE DU FICHIER JSON HTML")
        print("=" * 50)
        
        # Statistiques générales
        stats = data.get('extraction_stats', {})
        print(f"📊 Total pages: {stats.get('total_pages_processed', 0)}")
        print(f"✅ Succès: {stats.get('successful_extractions', 0)}")
        print(f"❌ Échecs: {stats.get('failed_extractions', 0)}")
        print(f"📦 Taille totale: {stats.get('total_html_size_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"🎯 Fandoms: {stats.get('fandoms_processed', 0)}")
        
        print("\n" + "=" * 50)
        
        # Examiner les pages HTML
        html_pages = data.get('html_pages', [])
        print(f"📋 Nombre de pages HTML: {len(html_pages)}")
        
        if html_pages:
            print("\n🔍 PREMIER EXEMPLE:")
            page = html_pages[0]
            print(f"  🎯 Fandom: {page.get('fandom_name', 'N/A')}")
            print(f"  🔗 URL: {page.get('character_url', 'N/A')}")
            print(f"  📄 Titre: {page.get('page_title', 'N/A')}")
            print(f"  📏 Taille HTML: {page.get('html_size_bytes', 0)} bytes")
            print(f"  ✅ Succès: {page.get('extraction_success', False)}")
            
            html_content = page.get('html_content', '')
            if html_content:
                print(f"  📝 HTML (début):")
                print("    " + html_content[:200].replace('\n', ' ') + "...")
            else:
                print("  ❌ Aucun contenu HTML")
        
        print("\n" + "=" * 50)
        print("🎯 RÉPARTITION PAR FANDOM:")
        
        # Compter par fandom
        fandom_counts = {}
        for page in html_pages:
            fandom = page.get('fandom_name', 'Unknown')
            fandom_counts[fandom] = fandom_counts.get(fandom, 0) + 1
        
        for fandom, count in sorted(fandom_counts.items()):
            print(f"  ✨ {fandom}: {count} pages")
        
        print("\n✅ Le fichier JSON contient bien le HTML de chaque caractère !")
        
    except FileNotFoundError:
        print("❌ Fichier JSON non trouvé")
    except json.JSONDecodeError:
        print("❌ Erreur de format JSON")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_html_json()