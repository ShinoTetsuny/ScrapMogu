import scrapy
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from ..items import CharacterItem


class CharacterScraperSpider(scrapy.Spider):
    name = 'character_scraper'
    allowed_domains = ['fandom.com']
    
    def __init__(self, *args, **kwargs):
        super(CharacterScraperSpider, self).__init__(*args, **kwargs)
        self.characters_data = []
        
    def start_requests(self):
        """Charge les URLs des pages de personnages depuis FinalResult.json"""
        try:
            with open('reports/FinalResult.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for fandom_result in data['results']:
                if fandom_result.get('characters_page_found') and fandom_result.get('characters_page_url'):
                    yield scrapy.Request(
                        url=fandom_result['characters_page_url'],
                        callback=self.parse_characters_page,
                        meta={
                            'fandom_name': fandom_result['fandom_name'],
                            'fandom_url': fandom_result['fandom_url']
                        }
                    )
                    
        except FileNotFoundError:
            self.logger.error("Fichier FinalResult.json non trouvé")
            return
            
    def parse_characters_page(self, response):
        """Parse la page des personnages et extrait les liens vers les 5 premiers personnages"""
        fandom_name = response.meta['fandom_name']
        fandom_url = response.meta['fandom_url']
        
        self.logger.info(f"Extraction des personnages pour {fandom_name}")
        
        # Stratégies pour trouver les liens de personnages individuels
        character_links = self.extract_character_links(response)
        
        # Prendre les 20 premiers
        first_twenty_links = character_links[:20]
        
        self.logger.info(f"🎯 {fandom_name}: {len(first_twenty_links)}/20 personnages à extraire")
        
        for i, character_url in enumerate(first_twenty_links):
            yield scrapy.Request(
                url=character_url,
                callback=self.parse_character_detail,
                meta={
                    'fandom_name': fandom_name,
                    'fandom_url': fandom_url,
                    'character_index': i + 1
                }
            )
    
    def extract_character_links(self, response):
        """Extrait les liens vers les pages individuelles de personnages"""
        character_links = set()
        base_url = response.url
        
        # Stratégie 1: Liens dans les listes de personnages
        list_links = response.css('.mw-category-group li a::attr(href), .category-page__members a::attr(href)').getall()
        for link in list_links:
            full_url = urljoin(base_url, link)
            if self.is_valid_character_link(full_url):
                character_links.add(full_url)
        
        # Stratégie 2: Liens dans les galleries et grilles
        gallery_links = response.css('.wikia-gallery-item a::attr(href), .gallery a::attr(href)').getall()
        for link in gallery_links:
            full_url = urljoin(base_url, link)
            if self.is_valid_character_link(full_url):
                character_links.add(full_url)
        
        # Stratégie 3: Liens généiques vers des pages wiki
        all_wiki_links = response.css('a[href*="/wiki/"]::attr(href)').getall()
        for link in all_wiki_links:
            full_url = urljoin(base_url, link)
            if self.is_valid_character_link(full_url):
                character_links.add(full_url)
        
        # Convertir en liste et limiter
        return list(character_links)[:50]  # Max 50 pour éviter les abus
    
    def is_valid_character_link(self, url):
        """Vérifie si un lien semble pointer vers une page de personnage valide"""
        if not url or '/wiki/' not in url:
            return False
            
        # Exclure les pages système et méta
        exclude_patterns = [
            'category:', 'template:', 'file:', 'help:', 'special:', 
            'user:', 'talk:', 'project:', 'mediawiki:', 'forum:',
            'blog:', 'thread:', 'list_of', 'list%20of'
        ]
        
        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in exclude_patterns)
    
    def parse_character_detail(self, response):
        """Parse les détails d'un personnage individuel"""
        fandom_name = response.meta['fandom_name']
        fandom_url = response.meta['fandom_url']
        character_index = response.meta['character_index']
        
        item = CharacterItem()
        
        # Données de base
        item['fandom_name'] = fandom_name
        item['fandom_url'] = fandom_url
        item['character_url'] = response.url
        item['scraping_timestamp'] = datetime.now().isoformat()
        item['scraping_success'] = True
        
        try:
            # Extraire le nom du personnage
            item['name'] = self.extract_character_name(response)
            
            # Extraire l'image principale
            item['image_url'] = self.extract_character_image(response)
            
            # Extraire la description/biographie
            item['description'] = self.extract_character_description(response)
            
            # Extraire les attributs spécifiques selon le type de fandom
            item['type_role_class'] = self.extract_character_type(response)
            item['attribute_1'] = self.extract_character_attribute_1(response)
            item['attribute_2'] = self.extract_character_attribute_2(response)
            
            self.logger.info(f"✅ {character_index}/20 - {item['name']} ({fandom_name})")
            
        except Exception as e:
            self.logger.warning(f"❌ {character_index}/20 - Erreur {fandom_name}: {e}")
            item['scraping_success'] = False
            item['name'] = f"Personnage_{character_index}_{fandom_name}"
            item['description'] = f"Erreur d'extraction: {str(e)}"
        
        yield item
    
    def extract_character_name(self, response):
        """Extrait le nom du personnage"""
        # Stratégies multiples pour le nom
        name_selectors = [
            'h1.page-header__title::text',
            'h1#firstHeading::text',
            'h1.firstHeading::text',
            '.page-title::text',
            'h1::text'
        ]
        
        for selector in name_selectors:
            name = response.css(selector).get()
            if name:
                return name.strip()
        
        # Fallback: extraire du titre de la page
        title = response.css('title::text').get()
        if title:
            # Enlever les suffixes wiki communs
            name = title.split(' | ')[0].split(' - ')[0].split(' (')[0]
            return name.strip()
        
        return "Nom inconnu"
    
    def extract_character_image(self, response):
        """Extrait l'URL de l'image principale du personnage"""
        # Recherche dans l'infobox
        infobox_images = response.css('.infobox img::attr(src), .portable-infobox img::attr(src)').getall()
        if infobox_images:
            return urljoin(response.url, infobox_images[0])
        
        # Recherche dans les galleries au début de page
        gallery_images = response.css('.wikia-gallery-item img::attr(src), .gallery img::attr(src)').getall()
        if gallery_images:
            return urljoin(response.url, gallery_images[0])
        
        # Recherche générale d'images
        all_images = response.css('img::attr(src)').getall()
        for img_src in all_images:
            if img_src and ('character' in img_src.lower() or 'portrait' in img_src.lower()):
                return urljoin(response.url, img_src)
        
        # Première image trouvée qui n'est pas un icône
        for img_src in all_images:
            if img_src and not any(x in img_src.lower() for x in ['icon', 'logo', 'button', 'arrow']):
                full_url = urljoin(response.url, img_src)
                if 'static.wikia' in full_url or 'fandom.com' in full_url:
                    return full_url
        
        return None
    
    def extract_character_description(self, response):
        """Extrait la description/biographie du personnage"""
        # Recherche de sections de description
        description_selectors = [
            '.mw-parser-output > p:first-of-type::text',
            '.character-description::text',
            '.biography::text',
            '#Biography + p::text',
            '.article-content p:first-of-type::text'
        ]
        
        for selector in description_selectors:
            desc = response.css(selector).get()
            if desc and len(desc.strip()) > 20:
                return desc.strip()[:500]  # Limiter à 500 caractères
        
        # Fallback: premier paragraphe avec du texte
        paragraphs = response.css('p::text').getall()
        for p in paragraphs:
            if p and len(p.strip()) > 30:
                return p.strip()[:500]
        
        return "Description non disponible"
    
    def extract_character_type(self, response):
        """Extrait le type/rôle/classe du personnage"""
        # Recherche dans l'infobox
        infobox_data = response.css('.infobox td::text, .portable-infobox .pi-data-value::text').getall()
        
        type_keywords = ['type', 'class', 'role', 'species', 'occupation', 'profession', 'rank']
        
        for i, data in enumerate(infobox_data):
            if any(keyword in data.lower() for keyword in type_keywords):
                # Prendre la valeur suivante
                if i + 1 < len(infobox_data):
                    return infobox_data[i + 1].strip()
        
        return "Type inconnu"
    
    def extract_character_attribute_1(self, response):
        """Extrait le premier attribut structuré"""
        # Recherche d'attributs dans l'infobox
        labels = response.css('.infobox th::text, .portable-infobox .pi-data-label::text').getall()
        values = response.css('.infobox td::text, .portable-infobox .pi-data-value::text').getall()
        
        if labels and values and len(labels) > 0:
            return f"{labels[0].strip()}: {values[0].strip()}" if len(values) > 0 else labels[0].strip()
        
        return "Attribut 1 non disponible"
    
    def extract_character_attribute_2(self, response):
        """Extrait le deuxième attribut structuré"""
        labels = response.css('.infobox th::text, .portable-infobox .pi-data-label::text').getall()
        values = response.css('.infobox td::text, .portable-infobox .pi-data-value::text').getall()
        
        if labels and values and len(labels) > 1:
            return f"{labels[1].strip()}: {values[1].strip()}" if len(values) > 1 else labels[1].strip()
        
        return "Attribut 2 non disponible"