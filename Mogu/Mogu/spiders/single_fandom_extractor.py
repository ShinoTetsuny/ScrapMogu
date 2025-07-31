import scrapy
import json
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path


class SingleFandomExtractorSpider(scrapy.Spider):
    name = 'single_fandom_extractor'
    allowed_domains = ['fandom.com']
    
    def __init__(self, fandom_url=None, fandom_name=None, request_file=None, *args, **kwargs):
        super(SingleFandomExtractorSpider, self).__init__(*args, **kwargs)
        self.fandom_url = fandom_url
        self.fandom_name = fandom_name
        self.request_file = request_file
        self.characters_extracted = 0
        self.characters_failed = 0
        
        # Créer le dossier data s'il n'existe pas
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        if not self.fandom_url:
            raise ValueError("fandom_url est requis")
            
    def start_requests(self):
        """Démarre par la page principale du fandom pour trouver les personnages"""
        self.logger.info(f"🎯 Extraction des personnages pour: {self.fandom_name}")
        self.logger.info(f"🔗 URL: {self.fandom_url}")
        
        yield scrapy.Request(
            url=self.fandom_url,
            callback=self.find_characters_page,
            meta={'fandom_name': self.fandom_name, 'fandom_url': self.fandom_url}
        )
    
    def find_characters_page(self, response):
        """Trouve la page des personnages du fandom"""
        fandom_name = response.meta['fandom_name']
        
        self.logger.info(f"🔍 Recherche de la page des personnages pour {fandom_name}")
        
        # Stratégies pour trouver les pages de personnages
        character_page_url = self.find_character_page(response)
        
        if character_page_url:
            self.logger.info(f"📋 Page des personnages trouvée: {character_page_url}")
            yield scrapy.Request(
                url=character_page_url,
                callback=self.extract_character_links,
                meta=response.meta
            )
        else:
            self.logger.warning(f"❌ Aucune page de personnages trouvée pour {fandom_name}")
    
    def find_character_page(self, response):
        """Utilise plusieurs stratégies pour trouver la page des personnages"""
        base_url = response.url
        
        # Mots-clés pour les personnages
        character_keywords = [
            'characters', 'character', 'personnages', 'personnage',
            'heroes', 'villains', 'people', 'cast', 'roster',
            'fighters', 'champions', 'members', 'list of characters',
            'category:characters', 'category:character'
        ]
        
        for keyword in character_keywords:
            # Recherche dans les liens avec XPath
            xpath_query = f'//a[contains(@href, "{keyword}")]/@href'
            links = response.xpath(xpath_query).getall()
            if links:
                return urljoin(base_url, links[0])
            
            # Recherche dans le texte des liens
            text_xpath = f'//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{keyword.lower()}")]/@href'
            text_links = response.xpath(text_xpath).getall()
            if text_links:
                return urljoin(base_url, text_links[0])
        
        # Recherche dans les menus de navigation
        nav_links = response.css('nav a::attr(href), .navigation a::attr(href), .menu a::attr(href)').getall()
        for link in nav_links:
            if any(keyword.lower() in link.lower() for keyword in character_keywords):
                return urljoin(base_url, link)
        
        # URLs de catégories communes
        category_patterns = [
            '/wiki/Category:Characters',
            '/wiki/Characters',
            '/wiki/Character_List',
            '/wiki/List_of_Characters'
        ]
        
        for pattern in category_patterns:
            potential_url = urljoin(base_url, pattern)
            return potential_url
        
        return None
    
    def extract_character_links(self, response):
        """Extrait tous les liens vers les personnages individuels"""
        fandom_name = response.meta['fandom_name']
        
        self.logger.info(f"📖 Extraction des liens de personnages pour {fandom_name}")
        
        # Récupérer tous les liens de personnages
        character_links = self.get_character_links(response)
        
        self.logger.info(f"🎯 {len(character_links)} personnages trouvés pour {fandom_name}")
        
        # Limiter à 2 personnages par fandom
        for i, character_url in enumerate(character_links[:2]):
            yield scrapy.Request(
                url=character_url,
                callback=self.extract_single_character,
                meta={
                    'fandom_name': fandom_name,
                    'fandom_url': self.fandom_url,
                    'character_index': i + 1,
                    'total_characters': len(character_links)
                }
            )
    
    def get_character_links(self, response):
        """Récupère les liens vers les pages de personnages individuels"""
        character_links = set()
        base_url = response.url
        
        # Stratégie 1: Liens dans les listes de catégories
        list_links = response.css('.mw-category-group li a::attr(href), .category-page__members a::attr(href)').getall()
        for link in list_links:
            full_url = urljoin(base_url, link)
            if self.is_valid_character_link(full_url):
                character_links.add(full_url)
        
        # Stratégie 2: Liens dans les galleries
        gallery_links = response.css('.wikia-gallery-item a::attr(href), .gallery a::attr(href)').getall()
        for link in gallery_links:
            full_url = urljoin(base_url, link)
            if self.is_valid_character_link(full_url):
                character_links.add(full_url)
        
        # Stratégie 3: Tous les liens wiki
        all_wiki_links = response.css('a[href*="/wiki/"]::attr(href)').getall()
        for link in all_wiki_links:
            full_url = urljoin(base_url, link)
            if self.is_valid_character_link(full_url):
                character_links.add(full_url)
        
        return list(character_links)
    
    def is_valid_character_link(self, url):
        """Vérifie si un lien est valide pour un personnage"""
        if not url or '/wiki/' not in url:
            return False
            
        exclude_patterns = [
            'category:', 'template:', 'file:', 'help:', 'special:', 
            'user:', 'talk:', 'project:', 'mediawiki:', 'forum:',
            'blog:', 'thread:', 'list_of', 'list%20of'
        ]
        
        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in exclude_patterns)
    
    def extract_single_character(self, response):
        """Extrait les données d'un personnage individuel et sauvegarde en JSON"""
        fandom_name = response.meta['fandom_name']
        character_index = response.meta['character_index']
        total_characters = response.meta['total_characters']
        
        try:
            # Extraire le HTML de la page principale
            page_main = response.css('.page__main').get()
            
            if not page_main:
                # Fallback vers d'autres sélecteurs
                page_main = response.css('.mw-parser-output').get() or \
                          response.css('.article-content').get() or \
                          response.css('.content').get() or \
                          response.css('main').get()
            
            # Extraire les informations de base
            character_data = {
                'character_info': {
                    'name': self.extract_character_name(response),
                    'title': self.extract_page_title(response),
                    'url': response.url,
                    'image_url': self.extract_character_image(response),
                    'description': self.extract_character_description(response)
                },
                'fandom_info': {
                    'name': fandom_name,
                    'url': self.fandom_url
                },
                'extraction_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'character_index': character_index,
                    'total_characters_in_fandom': total_characters,
                    'extraction_success': page_main is not None,
                    'html_size_bytes': len(page_main) if page_main else 0
                },
                'html_content': page_main
            }
            
            # Créer un nom de fichier unique
            safe_character_name = self.sanitize_filename(character_data['character_info']['name'])
            safe_fandom_name = self.sanitize_filename(fandom_name)
            
            filename = f"{safe_fandom_name}_{safe_character_name}_{character_index}.json"
            filepath = self.data_dir / filename
            
            # Sauvegarder le JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, indent=2, ensure_ascii=False)
            
            self.characters_extracted += 1
            
            self.logger.info(f"✅ {character_index}/{total_characters} - {character_data['character_info']['name']} ({fandom_name}) → {filename}")
            
        except Exception as e:
            self.characters_failed += 1
            self.logger.error(f"❌ {character_index}/{total_characters} - Erreur extraction {fandom_name}: {e}")
    
    def extract_character_name(self, response):
        """Extrait le nom du personnage"""
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
        
        # Fallback depuis l'URL
        try:
            return response.url.split('/')[-1].replace('_', ' ')
        except:
            return "Nom inconnu"
    
    def extract_page_title(self, response):
        """Extrait le titre de la page"""
        title = response.css('title::text').get()
        if title:
            title = title.strip()
            if '|' in title:
                title = title.split('|')[0].strip()
            return title
        return "Titre inconnu"
    
    def extract_character_image(self, response):
        """Extrait l'URL de l'image principale"""
        # Recherche dans l'infobox
        infobox_images = response.css('.infobox img::attr(src), .portable-infobox img::attr(src)').getall()
        if infobox_images:
            return urljoin(response.url, infobox_images[0])
        
        # Première image trouvée
        all_images = response.css('img::attr(src)').getall()
        for img_src in all_images:
            if img_src and 'static.wikia' in img_src:
                return urljoin(response.url, img_src)
        
        return None
    
    def extract_character_description(self, response):
        """Extrait la description du personnage"""
        desc_selectors = [
            '.mw-parser-output > p:first-of-type::text',
            '.character-description::text',
            '.biography::text'
        ]
        
        for selector in desc_selectors:
            desc = response.css(selector).get()
            if desc and len(desc.strip()) > 20:
                return desc.strip()[:500]
        
        # Fallback
        paragraphs = response.css('p::text').getall()
        for p in paragraphs:
            if p and len(p.strip()) > 30:
                return p.strip()[:500]
        
        return "Description non disponible"
    
    def sanitize_filename(self, name):
        """Nettoie un nom pour qu'il soit utilisable comme nom de fichier"""
        import re
        # Remplacer les caractères interdits
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', str(name))
        # Limiter la longueur
        return safe_name[:50]
    
    def closed(self, reason):
        """Appelé à la fermeture du spider"""
        self.logger.info("=" * 60)
        self.logger.info(f"🎉 EXTRACTION TERMINÉE POUR {self.fandom_name}")
        self.logger.info("=" * 60)
        self.logger.info(f"✅ Personnages extraits: {self.characters_extracted}")
        self.logger.info(f"❌ Échecs: {self.characters_failed}")
        self.logger.info(f"📁 Fichiers sauvegardés dans: {self.data_dir.absolute()}")
        
        if self.characters_extracted > 0:
            success_rate = (self.characters_extracted / (self.characters_extracted + self.characters_failed)) * 100
            self.logger.info(f"📈 Taux de succès: {success_rate:.1f}%")
        
        self.logger.info("=" * 60)