import scrapy
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from ..items import FandomAnalysisItem


class FandomAnalyzerSpider(scrapy.Spider):
    name = 'fandom_analyzer'
    allowed_domains = ['fandom.com']
    
    def __init__(self, test_mode=False, *args, **kwargs):
        super(FandomAnalyzerSpider, self).__init__(*args, **kwargs)
        self.results = []
        self.test_mode = test_mode
        
    def start_requests(self):
        """Charge la liste des fandoms et démarre les requêtes"""
        # Choisir le fichier selon le mode
        filename = 'test_fandoms.json' if self.test_mode else 'fandom_urls_json.json'
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Fichier {filename} non trouvé")
            return
        
        for fandom_url in data['fandom_urls']:
            yield scrapy.Request(
                url=fandom_url,
                callback=self.parse_fandom_homepage,
                meta={'fandom_url': fandom_url}
            )
    
    def parse_fandom_homepage(self, response):
        """Analyse la page d'accueil d'un fandom pour trouver les pages de personnages"""
        fandom_url = response.meta['fandom_url']
        fandom_name = self.extract_fandom_name(fandom_url)
        
        # Créer l'item d'analyse
        item = FandomAnalysisItem()
        item['fandom_name'] = fandom_name
        item['fandom_url'] = fandom_url
        item['analysis_timestamp'] = datetime.now().isoformat()
        item['characters_page_found'] = False
        item['characters_page_url'] = None
        item['characters_count'] = 0
        item['error_message'] = None
        
        try:
            # Stratégies pour trouver les pages de personnages
            character_page_url = self.find_character_page(response)
            
            if character_page_url:
                item['characters_page_found'] = True
                item['characters_page_url'] = character_page_url
                
                # Faire une requête vers la page des personnages pour compter
                yield scrapy.Request(
                    url=character_page_url,
                    callback=self.count_characters,
                    meta={'item': item}
                )
            else:
                self.logger.info(f"Aucune page de personnages trouvée pour {fandom_name}")
                yield item
                
        except Exception as e:
            item['error_message'] = str(e)
            self.logger.error(f"Erreur lors de l'analyse de {fandom_name}: {e}")
            yield item
    
    def find_character_page(self, response):
        """Utilise plusieurs stratégies pour trouver la page des personnages"""
        base_url = response.url
        
        # Stratégie 1: Recherche de liens avec des mots-clés spécifiques
        character_keywords = [
            'characters', 'character', 'personnages', 'personnage',
            'heroes', 'villains', 'people', 'cast', 'roster',
            'fighters', 'champions', 'members', 'list of characters',
            'category:characters', 'category:character'
        ]
        
        for keyword in character_keywords:
            # Recherche dans les liens avec XPath (plus sûr que CSS pour les attributs complexes)
            xpath_query = f'//a[contains(@href, "{keyword}")]/@href'
            links = response.xpath(xpath_query).getall()
            if links:
                return urljoin(base_url, links[0])
            
            # Recherche dans le texte des liens
            text_xpath = f'//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{keyword.lower()}")]/@href'
            text_links = response.xpath(text_xpath).getall()
            if text_links:
                return urljoin(base_url, text_links[0])
        
        # Stratégie 2: Recherche dans les catégories et menus de navigation
        nav_links = response.css('nav a::attr(href), .navigation a::attr(href), .menu a::attr(href)').getall()
        for link in nav_links:
            if any(keyword.lower() in link.lower() for keyword in character_keywords):
                return urljoin(base_url, link)
        
        # Stratégie 3: Recherche de pages de catégories communes
        category_patterns = [
            '/wiki/Category:Characters',
            '/wiki/Characters',
            '/wiki/Character_List',
            '/wiki/List_of_Characters',
            '/wiki/Category:People',
            '/wiki/Roster'
        ]
        
        for pattern in category_patterns:
            potential_url = urljoin(base_url, pattern)
            # On ne peut pas vérifier si la page existe ici, on retourne la première trouvée
            # La vérification se fera dans count_characters
            return potential_url
        
        return None
    
    def count_characters(self, response):
        """Compte le nombre de personnages sur la page des personnages"""
        item = response.meta['item']
        
        try:
            # Différentes stratégies pour compter les personnages
            character_count = 0
            
            # Stratégie 1: Compter les liens vers des pages de personnages individuels
            character_links = response.css('a[href*="/wiki/"]').getall()
            
            # Filtrer les liens qui semblent être des personnages (éviter les pages système)
            valid_character_links = []
            exclude_patterns = [
                'category:', 'template:', 'file:', 'help:', 'special:', 
                'user:', 'talk:', 'project:', 'mediawiki:'
            ]
            
            for link_html in character_links:
                href_match = re.search(r'href="([^"]*)"', link_html)
                if href_match:
                    href = href_match.group(1).lower()
                    if not any(pattern in href for pattern in exclude_patterns):
                        valid_character_links.append(href)
            
            character_count = len(set(valid_character_links))  # Éviter les doublons
            
            # Si peu de résultats, essayer une autre approche
            if character_count < 5:
                # Compter les éléments de liste ou de grille
                list_items = response.css('li, .character-item, .char-box, .member-box').getall()
                if len(list_items) > character_count:
                    character_count = len(list_items)
            
            item['characters_count'] = character_count
            self.logger.info(f"Trouvé {character_count} personnages pour {item['fandom_name']}")
            
        except Exception as e:
            item['error_message'] = f"Erreur lors du comptage: {str(e)}"
            self.logger.error(f"Erreur lors du comptage pour {item['fandom_name']}: {e}")
        
        yield item
    
    def extract_fandom_name(self, url):
        """Extrait le nom du fandom depuis l'URL"""
        parsed = urlparse(url)
        # Exemple: marvel.fandom.com -> marvel
        subdomain = parsed.netloc.split('.')[0]
        return subdomain.capitalize()
    
    def closed(self, reason):
        """Appelée à la fermeture du spider pour générer un rapport final"""
        self.logger.info(f"Spider fermé: {reason}")
        
        # Les statistiques finales seront visibles dans les logs et fichiers de sortie
        total_fandoms = len(self.results) if hasattr(self, 'results') else 0
        self.logger.info(f"Analyse terminée pour {total_fandoms} fandoms")