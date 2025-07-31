# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from .items import FandomAnalysisItem, CharacterItem


class FandomAnalysisPipeline:
    """Pipeline pour traiter les résultats d'analyse des fandoms"""
    
    def __init__(self):
        self.results = []
        self.stats = {
            'total_fandoms': 0,
            'successful_fandoms': 0,
            'fandoms_with_characters': 0,
            'total_characters_found': 0,
            'errors': 0
        }
    
    def process_item(self, item, spider):
        if isinstance(item, FandomAnalysisItem):
            adapter = ItemAdapter(item)
            
            # Mise à jour des statistiques
            self.stats['total_fandoms'] += 1
            
            if adapter.get('error_message'):
                self.stats['errors'] += 1
            else:
                self.stats['successful_fandoms'] += 1
                
                if adapter.get('characters_page_found'):
                    self.stats['fandoms_with_characters'] += 1
                    self.stats['total_characters_found'] += adapter.get('characters_count', 0)
            
            # Sauvegarder le résultat
            self.results.append(dict(adapter))
            
        return item
    
    def close_spider(self, spider):
        """Génère le rapport final quand le spider se ferme"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarder les résultats détaillés en JSON
        json_filename = f"reports/fandom_analysis_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'stats': self.stats,
                'results': self.results,
                'analysis_date': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # Créer un rapport CSV pour Excel
        csv_filename = f"reports/fandom_analysis_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            if self.results:
                writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                writer.writeheader()
                writer.writerows(self.results)
        
        # Afficher le rapport dans les logs
        spider.logger.info("=" * 60)
        spider.logger.info("RAPPORT FINAL D'ANALYSE DES FANDOMS")
        spider.logger.info("=" * 60)
        spider.logger.info(f"Total des fandoms analysés: {self.stats['total_fandoms']}")
        spider.logger.info(f"Fandoms analysés avec succès: {self.stats['successful_fandoms']}")
        spider.logger.info(f"Fandoms avec pages de personnages: {self.stats['fandoms_with_characters']}")
        spider.logger.info(f"Total des personnages trouvés: {self.stats['total_characters_found']}")
        spider.logger.info(f"Erreurs rencontrées: {self.stats['errors']}")
        
        if self.stats['successful_fandoms'] > 0:
            success_rate = (self.stats['fandoms_with_characters'] / self.stats['successful_fandoms']) * 100
            spider.logger.info(f"Taux de succès de détection: {success_rate:.1f}%")
        
        spider.logger.info(f"Rapport détaillé sauvegardé: {json_filename}")
        spider.logger.info(f"Rapport CSV sauvegardé: {csv_filename}")
        spider.logger.info("=" * 60)


class CharacterPipeline:
    """Pipeline pour traiter les données des personnages avec filtrage et nettoyage"""
    
    def __init__(self):
        self.characters = []
        self.stats = {
            'total_characters_processed': 0,
            'characters_filtered_out': 0,
            'characters_accepted': 0,
            'names_corrected_from_attributes': 0,
            'characters_with_images': 0,
            'characters_by_fandom': {}
        }
    
    def process_item(self, item, spider):
        if isinstance(item, CharacterItem):
            adapter = ItemAdapter(item)
            
            # Mise à jour des statistiques globales
            self.stats['total_characters_processed'] += 1
            fandom = adapter.get('fandom_name', 'Unknown')
            
            # Tentative de correction du nom depuis les attributs
            name = self.extract_valid_name(adapter, spider)
            
            # Filtrage : rejeter les personnages sans nom valide
            if not name or self.is_invalid_name(name):
                self.stats['characters_filtered_out'] += 1
                spider.logger.debug(f"Personnage filtré dans {fandom}: nom invalide '{name}'")
                raise DropItem(f"Personnage rejeté: nom invalide '{name}' dans {fandom}")
            
            # Mettre à jour le nom corrigé
            adapter['name'] = name
            
            # Comptage par fandom
            if fandom not in self.stats['characters_by_fandom']:
                self.stats['characters_by_fandom'][fandom] = 0
            self.stats['characters_by_fandom'][fandom] += 1
            
            # Validation des autres champs
            self.clean_and_validate_fields(adapter, spider)
            
            # Compteurs de réussite
            self.stats['characters_accepted'] += 1
            
            if adapter.get('image_url'):
                self.stats['characters_with_images'] += 1
            
            # Sauvegarder le personnage
            self.characters.append(dict(adapter))
        
        return item
    
    def extract_valid_name(self, adapter, spider):
        """Extrait un nom valide en vérifiant d'abord le champ name, puis les attributs"""
        
        # Vérifier le nom principal
        name = adapter.get('name', '').strip()
        if name and not self.is_invalid_name(name):
            return name
        
        # Chercher dans attribute_1
        attr1 = adapter.get('attribute_1', '')
        if attr1:
            potential_name = self.extract_name_from_attribute(attr1)
            if potential_name and not self.is_invalid_name(potential_name):
                self.stats['names_corrected_from_attributes'] += 1
                spider.logger.info(f"Nom corrigé depuis attribute_1: '{potential_name}'")
                return potential_name
        
        # Chercher dans attribute_2
        attr2 = adapter.get('attribute_2', '')
        if attr2:
            potential_name = self.extract_name_from_attribute(attr2)
            if potential_name and not self.is_invalid_name(potential_name):
                self.stats['names_corrected_from_attributes'] += 1
                spider.logger.info(f"Nom corrigé depuis attribute_2: '{potential_name}'")
                return potential_name
        
        return None
    
    def extract_name_from_attribute(self, attribute_text):
        """Extrait un nom potentiel depuis un attribut (format 'Label: Value')"""
        if ':' in attribute_text:
            # Format "Label: Value" - prendre la valeur
            parts = attribute_text.split(':', 1)
            if len(parts) == 2:
                return parts[1].strip()
        
        # Si pas de ':', retourner le texte tel quel
        return attribute_text.strip()
    
    def is_invalid_name(self, name):
        """Vérifie si un nom est invalide"""
        if not name or len(name.strip()) < 2:
            return True
        
        # Noms invalides courants
        invalid_names = [
            'nom inconnu', 'unknown', 'unnamed', 'name unknown',
            'personnage_', 'character_', 'n/a', 'none', 'null',
            'error', 'erreur', 'not found', 'missing', 'no name',
            'description non disponible', 'attribut', 'non disponible'
        ]
        
        name_lower = name.lower().strip()
        
        # Vérifier contre la liste des noms invalides
        for invalid in invalid_names:
            if invalid in name_lower:
                return True
        
        # Rejeter les noms qui sont seulement des chiffres
        if name.strip().isdigit():
            return True
            
        # Rejeter les noms trop courts (moins de 2 caractères)
        if len(name.strip()) < 2:
            return True
            
        return False
    
    def clean_and_validate_fields(self, adapter, spider):
        """Nettoie et valide les autres champs"""
        
        # Nettoyage de la description
        description = adapter.get('description', '').strip()
        if description and description != 'Description non disponible':
            # Supprimer les balises HTML basiques
            import re
            description = re.sub(r'<[^>]+>', '', description)
            # Limiter la longueur
            if len(description) > 1000:
                description = description[:1000] + "..."
            adapter['description'] = description
        else:
            adapter['description'] = "Description non disponible"
        
        # Nettoyage du type/rôle/classe
        type_role = adapter.get('type_role_class', '').strip()
        if not type_role or type_role == 'Type inconnu':
            adapter['type_role_class'] = "Type non spécifié"
        
        # Nettoyage des attributs
        for attr_key in ['attribute_1', 'attribute_2']:
            attr_value = adapter.get(attr_key, '').strip()
            if not attr_value or 'non disponible' in attr_value.lower():
                adapter[attr_key] = f"{attr_key.replace('_', ' ').title()} non spécifié"
        
        # Validation de l'URL d'image
        image_url = adapter.get('image_url')
        if image_url and not image_url.startswith(('http://', 'https://')):
            adapter['image_url'] = None
    
    def process_item(self, item, spider):
        if isinstance(item, CharacterItem):
            adapter = ItemAdapter(item)
            
            # Mise à jour des statistiques globales
            self.stats['total_characters_processed'] += 1
            fandom = adapter.get('fandom_name', 'Unknown')
            
            # Tentative de correction du nom depuis les attributs
            name = self.extract_valid_name(adapter, spider)
            
            # Filtrage : rejeter les personnages sans nom valide
            if not name or self.is_invalid_name(name):
                self.stats['characters_filtered_out'] += 1
                spider.logger.debug(f"🚫 Personnage filtré dans {fandom}: nom invalide '{name}'")
                raise DropItem(f"Personnage rejeté: nom invalide '{name}' dans {fandom}")
            
            # Mettre à jour le nom corrigé
            adapter['name'] = name
            
            # Comptage par fandom
            if fandom not in self.stats['characters_by_fandom']:
                self.stats['characters_by_fandom'][fandom] = 0
            self.stats['characters_by_fandom'][fandom] += 1
            
            # Validation des autres champs
            self.clean_and_validate_fields(adapter, spider)
            
            # Compteurs de réussite
            self.stats['characters_accepted'] += 1
            
            if adapter.get('image_url'):
                self.stats['characters_with_images'] += 1
            
            # Sauvegarder le personnage
            self.characters.append(dict(adapter))
            
            # Log progressif tous les 20 personnages
            if self.stats['characters_accepted'] % 20 == 0:
                spider.logger.info(f"🏁 Fandom {fandom} terminé! Total extraits: {self.stats['characters_accepted']}")
                self.log_current_stats(spider)
        
        return item
    
    def log_current_stats(self, spider):
        """Affiche les statistiques actuelles"""
        spider.logger.info(f"📊 Progression: {self.stats['characters_accepted']}/{self.stats['total_characters_processed']} acceptés")
        spider.logger.info(f"🚫 Filtrés: {self.stats['characters_filtered_out']}")
        spider.logger.info(f"📸 Avec images: {self.stats['characters_with_images']}")
        if self.stats['names_corrected_from_attributes'] > 0:
            spider.logger.info(f"🔧 Noms corrigés: {self.stats['names_corrected_from_attributes']}")
    
    def close_spider(self, spider):
        """Génère le rapport final des personnages"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarder les données des personnages
        characters_filename = f"reports/characters_sample_{timestamp}.json"
        with open(characters_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_stats': self.stats,
                'characters': self.characters,
                'extraction_date': datetime.now().isoformat(),
                'total_count': len(self.characters)
            }, f, indent=2, ensure_ascii=False)
        
        # Rapport final dans les logs
        spider.logger.info("=" * 60)
        spider.logger.info("🎉 RAPPORT FINAL D'EXTRACTION DES PERSONNAGES")
        spider.logger.info("=" * 60)
        spider.logger.info(f"📋 Total traités: {self.stats['total_characters_processed']}")
        spider.logger.info(f"✅ Personnages acceptés: {self.stats['characters_accepted']}")
        spider.logger.info(f"🚫 Personnages filtrés: {self.stats['characters_filtered_out']}")
        spider.logger.info(f"🔧 Noms corrigés depuis attributs: {self.stats['names_corrected_from_attributes']}")
        spider.logger.info(f"📸 Avec images: {self.stats['characters_with_images']}")
        
        if self.stats['total_characters_processed'] > 0:
            success_rate = (self.stats['characters_accepted'] / self.stats['total_characters_processed']) * 100
            spider.logger.info(f"📈 Taux d'acceptation: {success_rate:.1f}%")
        
        if self.stats['characters_accepted'] > 0:
            image_rate = (self.stats['characters_with_images'] / self.stats['characters_accepted']) * 100
            spider.logger.info(f"🖼️  Taux d'images: {image_rate:.1f}%")
        
        spider.logger.info("\n📊 Répartition par fandom:")
        for fandom, count in sorted(self.stats['characters_by_fandom'].items()):
            spider.logger.info(f"  ✨ {fandom}: {count} personnages")
        
        spider.logger.info(f"\n💾 Données sauvegardées: {characters_filename}")
        spider.logger.info("=" * 60)