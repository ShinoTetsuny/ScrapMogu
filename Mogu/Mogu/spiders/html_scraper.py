import scrapy
import json
from datetime import datetime
from urllib.parse import urljoin


class HtmlScraperSpider(scrapy.Spider):
    name = 'html_scraper'
    allowed_domains = ['fandom.com']
    
    def __init__(self, *args, **kwargs):
        super(HtmlScraperSpider, self).__init__(*args, **kwargs)
        self.html_data = []
        self.fandom_counts = {}  # Pour compter les personnages par fandom
        
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
        
        self.logger.info(f"🎯 {fandom_name}: Recherche des personnages...")
        
        # Initialiser le compteur pour ce fandom
        self.fandom_counts[fandom_name] = 0
        
        # Stratégies pour trouver les liens de personnages individuels
        character_links = self.extract_character_links(response)
        
        # Prendre seulement les 5 premiers
        first_five_links = character_links[:5]
        
        self.logger.info(f"📋 {fandom_name}: {len(first_five_links)} personnages trouvés")
        
        for i, character_url in enumerate(first_five_links):
            yield scrapy.Request(
                url=character_url,
                callback=self.parse_character_html,
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
        
        # Stratégie 3: Liens génériques vers des pages wiki
        all_wiki_links = response.css('a[href*="/wiki/"]::attr(href)').getall()
        for link in all_wiki_links:
            full_url = urljoin(base_url, link)
            if self.is_valid_character_link(full_url):
                character_links.add(full_url)
        
        # Convertir en liste et limiter
        return list(character_links)[:20]  # Max 20 pour avoir du choix
    
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
    
    def parse_character_html(self, response):
        """Récupère le HTML de la classe page__main"""
        fandom_name = response.meta['fandom_name']
        fandom_url = response.meta['fandom_url']
        character_index = response.meta['character_index']
        
        # Vérifier qu'on n'a pas déjà 5 personnages pour ce fandom
        if self.fandom_counts.get(fandom_name, 0) >= 5:
            self.logger.debug(f"⏭️ {fandom_name}: Limite de 5 personnages atteinte")
            return
        
        # Incrémenter le compteur
        self.fandom_counts[fandom_name] += 1
        
        try:
            # Extraire le contenu de la classe page__main
            page_main = response.css('.page__main').get()
            
            if not page_main:
                # Fallback: essayer d'autres sélecteurs communs
                page_main = response.css('.mw-parser-output').get() or \
                          response.css('.article-content').get() or \
                          response.css('.content').get() or \
                          response.css('main').get()
            
            if page_main:
                # Créer l'objet de données
                html_item = {
                    'fandom_name': fandom_name,
                    'fandom_url': fandom_url,
                    'character_url': response.url,
                    'character_index': character_index,
                    'page_title': self.extract_page_title(response),
                    'html_content': page_main,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'html_size_bytes': len(page_main),
                    'extraction_success': True
                }
                
                self.html_data.append(html_item)
                self.logger.info(f"✅ {character_index}/5 - HTML récupéré pour {fandom_name} ({len(page_main)} bytes)")
                
            else:
                self.logger.warning(f"❌ {character_index}/5 - Aucun contenu HTML trouvé pour {fandom_name}")
                # Sauvegarder quand même avec une erreur
                html_item = {
                    'fandom_name': fandom_name,
                    'fandom_url': fandom_url,
                    'character_url': response.url,
                    'character_index': character_index,
                    'page_title': self.extract_page_title(response),
                    'html_content': None,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'html_size_bytes': 0,
                    'extraction_success': False,
                    'error_message': 'Aucun contenu .page__main trouvé'
                }
                self.html_data.append(html_item)
                
        except Exception as e:
            self.logger.error(f"❌ {character_index}/5 - Erreur lors de l'extraction HTML pour {fandom_name}: {e}")
            # Sauvegarder l'erreur
            html_item = {
                'fandom_name': fandom_name,
                'fandom_url': fandom_url,
                'character_url': response.url,
                'character_index': character_index,
                'page_title': self.extract_page_title(response),
                'html_content': None,
                'extraction_timestamp': datetime.now().isoformat(),
                'html_size_bytes': 0,
                'extraction_success': False,
                'error_message': str(e)
            }
            self.html_data.append(html_item)
    
    def extract_page_title(self, response):
        """Extrait le titre de la page"""
        # Essayer plusieurs sélecteurs pour le titre
        title_selectors = [
            'h1.page-header__title::text',
            'h1#firstHeading::text',
            'h1.firstHeading::text',
            '.page-title::text',
            'h1::text',
            'title::text'
        ]
        
        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                # Nettoyer le titre
                title = title.strip()
                if '|' in title:
                    title = title.split('|')[0].strip()
                if '-' in title:
                    title = title.split('-')[0].strip()
                return title
        
        return "Titre inconnu"
    
    def closed(self, reason):
        """Sauvegarde les données HTML quand le spider se ferme"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarder les données HTML
        html_filename = f"reports/html_pages_{timestamp}.json"
        
        # Calculer les statistiques
        stats = {
            'total_pages_processed': len(self.html_data),
            'successful_extractions': sum(1 for item in self.html_data if item['extraction_success']),
            'failed_extractions': sum(1 for item in self.html_data if not item['extraction_success']),
            'total_html_size_bytes': sum(item['html_size_bytes'] for item in self.html_data),
            'fandoms_processed': len(self.fandom_counts),
            'pages_by_fandom': dict(self.fandom_counts),
            'extraction_date': datetime.now().isoformat()
        }
        
        # Sauvegarder le fichier JSON
        with open(html_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_stats': stats,
                'html_pages': self.html_data
            }, f, indent=2, ensure_ascii=False)
        
        # Afficher le rapport
        self.logger.info("=" * 60)
        self.logger.info("🎉 RAPPORT FINAL D'EXTRACTION HTML")
        self.logger.info("=" * 60)
        self.logger.info(f"📋 Total des pages traitées: {stats['total_pages_processed']}")
        self.logger.info(f"✅ Extractions réussies: {stats['successful_extractions']}")
        self.logger.info(f"❌ Extractions échouées: {stats['failed_extractions']}")
        self.logger.info(f"📦 Taille totale HTML: {stats['total_html_size_bytes'] / 1024 / 1024:.2f} MB")
        self.logger.info(f"🎯 Fandoms traités: {stats['fandoms_processed']}")
        
        if stats['total_pages_processed'] > 0:
            success_rate = (stats['successful_extractions'] / stats['total_pages_processed']) * 100
            self.logger.info(f"📈 Taux de succès: {success_rate:.1f}%")
        
        self.logger.info("\n📊 Répartition par fandom:")
        for fandom, count in sorted(stats['pages_by_fandom'].items()):
            self.logger.info(f"  ✨ {fandom}: {count} pages HTML")
        
        self.logger.info(f"\n💾 Données HTML sauvegardées: {html_filename}")
        self.logger.info("=" * 60)