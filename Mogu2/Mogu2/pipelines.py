# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
from datetime import datetime
from itemadapter import ItemAdapter


class FandomJsonPipeline:
    """Pipeline pour sauvegarder les items dans des fichiers JSON organisés par fandom"""
    
    def open_spider(self, spider):
        """Initialiser le pipeline au démarrage du spider"""
        self.fandom_name = spider.fandom_name
        self.items = []
        
        # Créer le dossier de sortie
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.result_dir = os.path.join(base_dir, 'result', self.fandom_name)
        os.makedirs(self.result_dir, exist_ok=True)
        
        # Nom du fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(self.result_dir, f'{self.fandom_name}_characters_{timestamp}.json')
        
        spider.logger.info(f"Sauvegarde des résultats dans: {self.filename}")
    
    def process_item(self, item, spider):
        """Traiter chaque item"""
        adapter = ItemAdapter(item)
        
        # Nettoyer et valider les données
        cleaned_item = {}
        for field, value in adapter.items():
            if value is not None:
                # Nettoyer les chaînes de caractères
                if isinstance(value, str):
                    cleaned_item[field] = value.strip()
                else:
                    cleaned_item[field] = value
            else:
                cleaned_item[field] = ""
        
        # Valider que les champs obligatoires sont présents
        required_fields = ['name', 'image_url']
        for field in required_fields:
            if not cleaned_item.get(field):
                spider.logger.warning(f"Champ obligatoire manquant '{field}' pour l'item: {cleaned_item}")
                return item  # Ne pas sauvegarder cet item
        
        self.items.append(cleaned_item)
        spider.logger.info(f"Item traité: {cleaned_item['name']}")
        
        return item
    
    def close_spider(self, spider):
        """Sauvegarder tous les items à la fermeture du spider"""
        if self.items:
            # Créer la structure de données finale
            output_data = {
                'fandom_name': self.fandom_name,
                'scraped_at': datetime.now().isoformat(),
                'total_characters': len(self.items),
                'characters': self.items
            }
            
            # Sauvegarder en JSON
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            spider.logger.info(f"Sauvegardé {len(self.items)} personnages dans {self.filename}")
        else:
            spider.logger.warning("Aucun personnage trouvé à sauvegarder")


class Mogu2Pipeline:
    def process_item(self, item, spider):
        return item
