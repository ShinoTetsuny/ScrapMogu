import scrapy
import re
import os
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
from ..items import FandomCharacterItem


class FandomSpider(scrapy.Spider):
    name = 'fandom_spider'
    allowed_domains = ['fandom.com']
    
    def __init__(self, start_url=None, max_characters=None, *args, **kwargs):
        super(FandomSpider, self).__init__(*args, **kwargs)
        
        if not start_url:
            raise ValueError("Vous devez fournir une URL de départ avec: -a start_url=https://...")
        
        self.start_urls = [start_url]
        self.base_url = start_url
        
        # Limite de personnages (défaut: 10)
        self.max_characters = int(max_characters) if max_characters else 10
        
        # Extraire le nom du fandom de l'URL
        parsed_url = urlparse(start_url)
        self.fandom_name = parsed_url.netloc.split('.')[0]
        
        # Flag pour arrêter le scraping dès qu'on atteint la limite
        self.limit_reached = False
        
        # Statistiques pour le rapport
        self.stats = {
            'pages_traitees': 0,
            'personnages_trouves': 0,
            'erreurs': [],
            'pages_ignorees': [],
            'start_time': datetime.now(),
            'max_characters': self.max_characters
        }
        
        self.logger.info(f"🎯 Limite fixée à {self.max_characters} personnages pour {self.fandom_name}")
        
        # Créer les dossiers de sortie
        self.setup_output_directories()
    
    def setup_output_directories(self):
        """Créer les dossiers result et report pour ce fandom"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        self.result_dir = os.path.join(base_dir, 'result', self.fandom_name)
        self.report_dir = os.path.join(base_dir, 'report', self.fandom_name)
        
        os.makedirs(self.result_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
    
    def start_requests(self):
        """Point d'entrée du spider"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_homepage,
                meta={'fandom_name': self.fandom_name}
            )
    
    def parse_homepage(self, response):
        """
        Étape 1: Recevoir le lien d'une page de fandom
        Étape 2: Récupérer les différents liens de navigation dans la div content
        Étape 3: Les lister et trier pour trouver les liens du type /wiki/Category:Characters
        """
        if self.limit_reached:
            self.logger.info("🛑 Limite atteinte, arrêt du parse_homepage")
            return
            
        self.logger.info(f"Parsing homepage: {response.url}")
        
        # Chercher les liens de navigation vers les catégories de personnages
        # Patterns courants pour les catégories de personnages
        character_patterns = [
            r'.*[Cc]haracters?.*',
            r'.*[Pp]ersonnages?.*',
            r'.*[Pp]eople.*',
            r'.*[Ii]ndividuals.*',
            r'.*[Bb]eings.*'
        ]
        
        # Extraire les liens depuis les zones de contenu principales basées sur la structure réelle
        content_selectors = [
            'div.mw-content-ltr.mw-parser-output',  # Zone principale de contenu
            'div#content.page-content',              # Container de contenu
            'div.content',                           # Container générique
            'main',                                  # Élément principal
            'body'                                   # Fallback
        ]
        
        content_area = None
        for selector in content_selectors:
            content_area = response.css(selector)
            if content_area:
                break
        
        if not content_area:
            self.logger.warning("Impossible de trouver la zone de contenu principale")
            return
        
        # Extraire tous les liens vers les catégories
        links = content_area.css('a[href*="/wiki/Category:"]::attr(href)').getall()
        character_category_links = []
        
        for link in links:
            if link:
                for pattern in character_patterns:
                    if re.search(pattern, link, re.IGNORECASE):
                        full_url = urljoin(response.url, link)
                        character_category_links.append(full_url)
                        break
        
        # Supprimer les doublons
        character_category_links = list(set(character_category_links))
        
        self.logger.info(f"Trouvé {len(character_category_links)} liens de catégories de personnages")
        
        # Si aucun lien trouvé avec les patterns, essayer une recherche plus directe
        if not character_category_links:
            # Chercher spécifiquement le lien "Characters"
            direct_character_links = content_area.css('a[href="/wiki/Category:Characters"]::attr(href)').getall()
            for link in direct_character_links:
                full_url = urljoin(response.url, link)
                character_category_links.append(full_url)
        
        if not character_category_links:
            self.logger.warning("Aucun lien de catégorie de personnages trouvé !")
            return
        
        # Suivre chaque lien de catégorie
        for category_url in character_category_links:
            if self.limit_reached:
                self.logger.info("🛑 Limite atteinte, arrêt du traitement des catégories")
                break
            yield scrapy.Request(
                url=category_url,
                callback=self.parse_character_category,
                meta={
                    'fandom_name': self.fandom_name,
                    'category_url': category_url
                }
            )
    
    def parse_character_category(self, response):
        """
        Étape 4: Aller sur la page où il y a la liste des personnages
        Étape 5: Si les liens sont encore des catégories, aller dessus pour la bonne liste
        """
        if self.limit_reached:
            self.logger.info("🛑 Limite atteinte, arrêt du parse_character_category")
            return
            
        self.logger.info(f"Parsing character category: {response.url}")
        self.stats['pages_traitees'] += 1
        
        # Chercher les liens vers les personnages avec les sélecteurs optimisés
        character_links = []
        
        # Sélecteurs basés sur la structure réelle observée
        member_selectors = [
            '.category-page__member-link::attr(href)',      # Sélecteur principal observé
            'div.category-page__members a::attr(href)',     # Container principal
            'li.category-page__member a::attr(href)',       # Éléments de liste
            'div.category-page-member a::attr(href)',       # Variation de classe
            'div.category-gallery-item a::attr(href)',      # Mode galerie
            'div.categorygallery a::attr(href)',            # Galerie alternative
        ]
        
        # Essayer chaque sélecteur jusqu'à trouver des liens
        for selector in member_selectors:
            links = response.css(selector).getall()
            if links:
                character_links.extend(links)
                self.logger.info(f"Trouvé {len(links)} liens avec le sélecteur: {selector}")
                break
        
        # Si pas de liens trouvés avec les sélecteurs spécifiques, fallback intelligent
        if not character_links:
            self.logger.warning("Aucun lien trouvé avec les sélecteurs spécifiques, utilisation du fallback")
            
            # Chercher dans toute la page mais filtrer intelligemment
            all_links = response.css('a[href*="/wiki/"]::attr(href)').getall()
            for link in all_links:
                if link and '/wiki/' in link:
                    # Éviter les pages système, templates, etc.
                    excluded_prefixes = [
                        '/wiki/Category:', '/wiki/Template:', '/wiki/File:', 
                        '/wiki/Special:', '/wiki/Help:', '/wiki/User:', 
                        '/wiki/Talk:', '/wiki/Project:'
                    ]
                    
                    if not any(link.startswith(prefix) for prefix in excluded_prefixes):
                        character_links.append(link)
        
        # Supprimer les doublons tout en préservant l'ordre
        character_links = list(dict.fromkeys(character_links))
        
        self.logger.info(f"Trouvé {len(character_links)} liens uniques de personnages")
        
        if not character_links:
            self.logger.warning(f"Aucun personnage trouvé sur la page: {response.url}")
            return
        
        # Traiter chaque lien
        for link in character_links:
            if self.limit_reached:
                self.logger.info("🛑 Limite atteinte, arrêt du traitement des liens")
                break
            if link:
                full_url = urljoin(response.url, link)
                
                # Vérifier si c'est encore une catégorie
                if '/wiki/Category:' in link:
                    # C'est une sous-catégorie, la suivre récursivement
                    if not self.limit_reached:
                        self.logger.info(f"Sous-catégorie détectée: {link}")
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse_character_category,
                            meta=response.meta
                        )
                else:
                    # Vérifier si on a atteint la limite avant de scraper plus de personnages
                    if self.limit_reached:
                        self.logger.info(f"🛑 Limite de {self.max_characters} personnages atteinte, arrêt du scraping")
                        return
                    
                    # C'est probablement une page de personnage
                    yield scrapy.Request(
                        url=full_url,
                        callback=self.parse_character_page,
                        meta=response.meta
                    )
    
    def parse_character_page(self, response):
        """
        Étape 6: Aller sur la page de chaque personnage
        Étape 7: Récupérer les données depuis l'infobox et le contenu principal
        """
        # Vérifier si on a déjà atteint la limite
        if self.limit_reached:
            self.logger.info(f"🛑 Limite déjà atteinte, arrêt du parse_character_page")
            return
        
        self.logger.info(f"Parsing character page: {response.url} ({self.stats['personnages_trouves']}/{self.max_characters})")
        self.stats['pages_traitees'] += 1
        
        try:
            item = FandomCharacterItem()
            
            # Métadonnées de base
            item['source_url'] = response.url
            item['fandom_name'] = response.meta.get('fandom_name', self.fandom_name)
            item['scraped_at'] = datetime.now().isoformat()
            
            # Nom du personnage (obligatoire)
            name = self.extract_character_name(response)
            if not name:
                self.logger.warning(f"Nom non trouvé pour {response.url}")
                self.stats['pages_ignorees'].append(response.url)
                return
            item['name'] = name
            
            # Image principale (obligatoire selon les exigences)
            image_url = self.extract_character_image(response)
            if not image_url:
                self.logger.warning(f"Image non trouvée pour {response.url} - page ignorée (image obligatoire)")
                self.stats['pages_ignorees'].append(response.url)
                return
            item['image_url'] = image_url
            
            # Description
            description = self.extract_character_description(response)
            item['description'] = description or "Description non disponible"
            
            # Type/Rôle/Classe
            character_type = self.extract_character_type(response)
            item['character_type'] = character_type or "Type non spécifié"
            
            # Attributs supplémentaires depuis l'infobox
            attributes = self.extract_additional_attributes(response)
            item['attribute1_name'] = attributes.get('attr1_name', 'Attribut 1')
            item['attribute1_value'] = attributes.get('attr1_value', 'Non spécifié')
            item['attribute2_name'] = attributes.get('attr2_name', 'Attribut 2')
            item['attribute2_value'] = attributes.get('attr2_value', 'Non spécifié')
            
            self.stats['personnages_trouves'] += 1
            self.logger.info(f"✅ Personnage {self.stats['personnages_trouves']}/{self.max_characters} extrait: {name}")
            yield item
            
            # Arrêter le spider si on a atteint la limite
            if self.stats['personnages_trouves'] >= self.max_characters:
                self.limit_reached = True  # Activer le flag pour empêcher toute nouvelle requête
                self.logger.info(f"🎯 Objectif atteint ! {self.max_characters} personnages extraits avec succès")
                self.crawler.engine.close_spider(self, '🎉 Limite de personnages atteinte')
            
        except Exception as e:
            error_msg = f"Erreur lors du parsing de {response.url}: {str(e)}"
            self.logger.error(error_msg)
            self.stats['erreurs'].append(error_msg)
            
            # Log détaillé pour le debug
            import traceback
            self.logger.debug(f"Trace complète: {traceback.format_exc()}")
    
    def extract_character_name(self, response):
        """Extraire le nom du personnage - Méthode adaptative universelle"""
        # ÉTAPE 1: Sélecteurs spécifiques observés sur différents fandoms
        specific_selectors = [
            'h1.page-header__title .mw-page-title-main::text',  # Fandom moderne
            'h1.page-header__title::text',                       # Fandom classique
            '.pi-title[data-source="name"]::text',              # Infobox portable
            '.infobox-title::text',                              # Infobox traditionnelle
            '.character-name::text',                             # Sélecteur dédié
            '#firstHeading .mw-page-title-main::text',          # MediaWiki standard
        ]
        
        # ÉTAPE 2: Sélecteurs génériques de titre
        generic_selectors = [
            'h1::text',
            '.page-title::text', 
            '.article-title::text',
            '.entry-title::text',
            '#firstHeading::text',
            '.mw-page-title-main::text'
        ]
        
        # ÉTAPE 3: Chercher dans les métadonnées
        meta_selectors = [
            'meta[property="og:title"]::attr(content)',
            'title::text'
        ]
        
        # Essayer les sélecteurs dans l'ordre de priorité
        all_selectors = specific_selectors + generic_selectors + meta_selectors
        
        for selector in all_selectors:
            try:
                name = response.css(selector).get()
                if name and name.strip():
                    cleaned_name = self.clean_character_name(name.strip())
                    if cleaned_name and len(cleaned_name) > 1:  # Éviter les noms trop courts
                        self.logger.info(f"✅ Nom trouvé avec {selector}: {cleaned_name}")
                        return cleaned_name
            except Exception as e:
                self.logger.debug(f"Erreur avec le sélecteur {selector}: {e}")
                continue
        
        # ÉTAPE 4: Extraction depuis l'URL en dernier recours
        url_parts = response.url.split('/')
        if url_parts and url_parts[-1]:
            url_name = url_parts[-1].replace('_', ' ').replace('%27', "'").replace('%20', ' ')
            cleaned_url_name = self.clean_character_name(url_name)
            if cleaned_url_name:
                self.logger.info(f"⚠️ Nom extrait de l'URL: {cleaned_url_name}")
                return cleaned_url_name
        
        return None
    
    def clean_character_name(self, name):
        """Nettoyer le nom du personnage"""
        if not name:
            return None
        
        # Supprimer les préfixes/suffixes courants
        prefixes_to_remove = [
            'Category:', 'File:', 'Template:', 'User:', 'Talk:', 'Special:',
            'Main Page', 'Home', 'Wiki'
        ]
        
        cleaned = name.strip()
        
        # Supprimer les préfixes
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                return None  # Ce n'est pas un nom de personnage
        
        # Nettoyer les caractères indésirables
        cleaned = cleaned.replace('\n', ' ').replace('\t', ' ').strip()
        
        # Supprimer les doublons d'espaces
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned if len(cleaned) > 1 else None
    
    def extract_character_image(self, response):
        """Extraire l'URL de l'image principale - Méthode adaptative universelle"""
        # ÉTAPE 1: Images prioritaires dans les infobox (plus fiables)
        priority_selectors = [
            # Infobox portable (structure moderne)
            '.portable-infobox .pi-image img::attr(src)',
            '.portable-infobox .pi-image img::attr(data-src)',
            '.portable-infobox img::attr(src)',
            '.portable-infobox img::attr(data-src)',
            
            # Infobox traditionnelle
            '.infobox img::attr(src)',
            '.infobox img::attr(data-src)',
            '.infobox-image img::attr(src)',
            '.infobox-image img::attr(data-src)',
            
            # Autres structures d'infobox
            '.character-infobox img::attr(src)',
            '.character-infobox img::attr(data-src)',
            '.info-box img::attr(src)',
            '.info-box img::attr(data-src)',
        ]
        
        # ÉTAPE 2: Images dans le contenu principal
        content_selectors = [
            # Premier paragraphe avec image
            '.mw-parser-output p:first-of-type img::attr(src)',
            '.mw-parser-output p:first-of-type img::attr(data-src)',
            
            # Zone de contenu principale
            '.mw-parser-output img::attr(src)',
            '.mw-parser-output img::attr(data-src)',
            
            # Content wrapper
            '.page-content img::attr(src)',
            '.page-content img::attr(data-src)',
            'main img::attr(src)',
            'main img::attr(data-src)',
        ]
        
        # ÉTAPE 3: Sélecteurs de fallback général
        fallback_selectors = [
            'img[alt*="portrait"]::attr(src)',
            'img[alt*="character"]::attr(src)', 
            'img[class*="character"]::attr(src)',
            'img[class*="portrait"]::attr(src)',
            'img[src*=".jpg"]::attr(src)',
            'img[src*=".png"]::attr(src)',
            'img[data-src*=".jpg"]::attr(data-src)',
            'img[data-src*=".png"]::attr(data-src)'
        ]
        
        # Tester les sélecteurs par ordre de priorité
        all_selector_groups = [
            ("infobox", priority_selectors),
            ("content", content_selectors), 
            ("fallback", fallback_selectors)
        ]
        
        for group_name, selectors in all_selector_groups:
            for selector in selectors:
                try:
                    images = response.css(selector).getall()
                    for img_url in images:
                        if img_url and self.is_valid_image_url(img_url):
                            full_url = urljoin(response.url, img_url)
                            self.logger.info(f"✅ Image trouvée ({group_name}) avec {selector}: {full_url}")
                            return full_url
                except Exception as e:
                    self.logger.debug(f"Erreur avec {selector}: {e}")
                    continue
        
        self.logger.warning("❌ Aucune image valide trouvée")
        return None
    
    def is_valid_image_url(self, url):
        """Vérifier si une URL d'image est valide pour un personnage"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        # ÉTAPE 1: Vérifier les extensions valides
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        has_valid_ext = any(ext in url_lower for ext in valid_extensions)
        
        if not has_valid_ext:
            return False
        
        # ÉTAPE 2: Éviter les images système et placeholder
        invalid_patterns = [
            'data:image/gif;base64',  # Images placeholder lazy-load
            'placeholder',
            'noimage', 
            'no-image',
            'default',
            'missing',
            '/icons/',
            '/ui/',
            '/commons/',
            'wiki.png',               # Logo du wiki
            'favicon',
            'logo',
            'edit-icon',
            'delete-icon',
            '1x1',                    # Images tracking
            'transparent',
            'spacer',
        ]
        
        # ÉTAPE 3: Éviter les très petites images (probablement des icônes)
        size_indicators = [
            '/width/1/', '/width/2/', '/width/3/', '/width/4/', '/width/5/',
            '/height/1/', '/height/2/', '/height/3/', '/height/4/', '/height/5/',
            'width=1', 'width=2', 'width=3', 'width=4', 'width=5',
            'height=1', 'height=2', 'height=3', 'height=4', 'height=5'
        ]
        
        # ÉTAPE 4: Vérifications
        is_system_image = any(pattern in url_lower for pattern in invalid_patterns)
        is_tiny_image = any(size in url_lower for size in size_indicators)
        
        # ÉTAPE 5: Critères de qualité pour privilégier les bonnes images
        quality_indicators = [
            '/latest/',               # Images récentes
            '/revision/',             # Images versionnées
            'character',              # Mot-clé personnage
            'portrait',               # Mot-clé portrait
            '/smart/',                # Images optimisées
        ]
        
        has_quality_indicator = any(indicator in url_lower for indicator in quality_indicators)
        
        # Retour avec logging pour debug
        is_valid = has_valid_ext and not is_system_image and not is_tiny_image
        
        if not is_valid:
            self.logger.debug(f"Image rejetée: {url} (system: {is_system_image}, tiny: {is_tiny_image})")
        elif has_quality_indicator:
            self.logger.debug(f"Image de qualité détectée: {url}")
        
        return is_valid
    
    def extract_character_description(self, response):
        """Extraire la description - Méthode adaptative universelle"""
        # ÉTAPE 1: Trouver la zone de contenu principale
        content_containers = [
            'div.mw-content-ltr.mw-parser-output',
            'div.mw-parser-output', 
            'div.page-content',
            'main.page__main',
            'div#content',
            'main',
            'article'
        ]
        
        content_area = None
        for container in content_containers:
            content_area = response.css(container)
            if content_area:
                break
        
        if not content_area:
            self.logger.warning("Aucune zone de contenu trouvée")
            return None
        
        # ÉTAPE 2: Sélecteurs adaptatifs pour la description
        description_strategies = [
            # Stratégie 1: Premier paragraphe significatif
            self.extract_first_paragraph,
            # Stratégie 2: Introduction ou summary
            self.extract_intro_section,
            # Stratégie 3: Paragraphes après infobox
            self.extract_post_infobox_content,
            # Stratégie 4: Fallback général
            self.extract_any_paragraph
        ]
        
        for strategy in description_strategies:
            try:
                description = strategy(content_area, response)
                if description and len(description.strip()) > 30:
                    self.logger.info(f"✅ Description trouvée avec {strategy.__name__}")
                    return self.clean_description(description)
            except Exception as e:
                self.logger.debug(f"Erreur avec {strategy.__name__}: {e}")
                continue
        
        return None
    
    def extract_first_paragraph(self, content_area, response):
        """Extraire le premier paragraphe significatif"""
        # Paragraphes qui ne sont pas dans l'infobox
        paragraphs = content_area.css('p:not(.pi-caption):not(.pi-data-value)::text').getall()
        
        for p in paragraphs:
            cleaned = p.strip()
            if len(cleaned) > 50 and not self.is_navigation_text(cleaned):
                return cleaned
        return None
    
    def extract_intro_section(self, content_area, response):
        """Chercher une section d'introduction"""
        intro_selectors = [
            '.intro::text',
            '.summary::text', 
            '.description::text',
            '.character-intro::text',
            'div[class*="intro"] p::text',
            'div[class*="summary"] p::text'
        ]
        
        for selector in intro_selectors:
            texts = content_area.css(selector).getall()
            if texts:
                combined = ' '.join([t.strip() for t in texts if t.strip()])
                if len(combined) > 30:
                    return combined
        return None
    
    def extract_post_infobox_content(self, content_area, response):
        """Extraire le contenu après l'infobox"""
        # Chercher tous les éléments p après l'infobox
        all_p = content_area.css('p').getall()
        
        # Essayer de trouver où l'infobox se termine
        collecting = False
        paragraphs = []
        
        for p_html in all_p:
            # Si on trouve une infobox, on commence à collecter après
            if 'infobox' in p_html or 'portable-infobox' in p_html:
                collecting = True
                continue
            
            if collecting:
                # Extraire le texte de ce paragraphe
                from scrapy import Selector
                p_text = Selector(text=p_html).css('::text').getall()
                text = ' '.join([t.strip() for t in p_text if t.strip()])
                
                if len(text) > 20:
                    paragraphs.append(text)
                    if len(paragraphs) >= 2:  # Prendre max 2 paragraphes
                        break
        
        return ' '.join(paragraphs) if paragraphs else None
    
    def extract_any_paragraph(self, content_area, response):
        """Fallback: n'importe quel paragraphe valide"""
        all_text = content_area.css('p::text').getall()
        
        for text in all_text:
            cleaned = text.strip()
            if len(cleaned) > 30 and not self.is_navigation_text(cleaned):
                return cleaned
        return None
    
    def is_navigation_text(self, text):
        """Déterminer si un texte est de la navigation plutôt qu'une description"""
        nav_indicators = [
            'see also', 'main article', 'for other uses', 'disambiguation',
            'category:', 'template:', 'click here', 'more info',
            'edit', 'view source', 'history', 'talk page'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in nav_indicators)
    
    def clean_description(self, description):
        """Nettoyer la description"""
        if not description:
            return None
        
        import re
        
        # Nettoyer les caractères de formatage
        cleaned = re.sub(r'\s+', ' ', description.strip())
        
        # Limiter la longueur
        if len(cleaned) > 500:
            cleaned = cleaned[:500] + "..."
        
        return cleaned
    
    def extract_character_type(self, response):
        """Extraire le type/rôle - Méthode adaptative universelle"""
        # ÉTAPE 1: Chercher dans différents types d'infobox
        infobox_selectors = [
            '.portable-infobox',
            '.infobox',
            '.character-infobox', 
            '.info-box',
            '.infobox-character',
            'table.infobox'
        ]
        
        # ÉTAPE 2: Labels possibles pour le type (multilingue)
        type_keywords = [
            # Anglais
            'species', 'race', 'type', 'class', 'occupation', 'job', 'role', 'profession',
            'affiliation', 'faction', 'group', 'allegiance', 'side', 'team',
            'origin', 'nationality', 'home', 'status', 'rank', 'title',
            
            # Français
            'espèce', 'classe', 'métier', 'rôle', 'profession', 'occupation',
            'groupe', 'faction', 'origine', 'nationalité', 'statut', 'rang', 'titre',
            
            # Espagnol
            'especie', 'raza', 'tipo', 'clase', 'profesión', 'trabajo', 'rol',
            'afiliación', 'grupo', 'origen', 'nacionalidad', 'estado'
        ]
        
        # ÉTAPE 3: Essayer chaque type d'infobox
        for infobox_selector in infobox_selectors:
            infobox = response.css(infobox_selector)
            if not infobox:
                continue
            
            # Méthode 1: Recherche par data-source
            for keyword in type_keywords:
                value = infobox.css(f'.pi-data[data-source="{keyword}"] .pi-data-value::text').get()
                if value and value.strip():
                    cleaned_value = value.strip()
                    self.logger.info(f"✅ Type trouvé par data-source '{keyword}': {cleaned_value}")
                    return cleaned_value
            
            # Méthode 2: Recherche par label de texte
            data_rows = infobox.css('.pi-data, tr')
            for row in data_rows:
                label_texts = row.css('.pi-data-label::text, th::text, td:first-child::text').getall()
                value_texts = row.css('.pi-data-value::text, td:last-child::text').getall()
                
                for label_text in label_texts:
                    if label_text:
                        label_lower = label_text.lower().strip()
                        for keyword in type_keywords:
                            if keyword in label_lower:
                                # Trouver la valeur correspondante
                                for value_text in value_texts:
                                    if value_text and value_text.strip():
                                        cleaned_value = value_text.strip()
                                        self.logger.info(f"✅ Type trouvé par label '{label_text}': {cleaned_value}")
                                        return cleaned_value
            
            # Méthode 3: Patterns HTML spécifiques
            html_patterns = [
                f'{infobox_selector} tr:contains("Species") td::text',
                f'{infobox_selector} tr:contains("Type") td::text',
                f'{infobox_selector} tr:contains("Class") td::text',
                f'{infobox_selector} tr:contains("Race") td::text',
                f'{infobox_selector} tr:contains("Occupation") td::text'
            ]
            
            for pattern in html_patterns:
                try:
                    values = response.css(pattern).getall()
                    for value in values:
                        if value and value.strip():
                            cleaned_value = value.strip()
                            self.logger.info(f"✅ Type trouvé par pattern HTML: {cleaned_value}")
                            return cleaned_value
                except:
                    continue
        
        # ÉTAPE 4: Chercher dans les catégories de la page
        categories = response.css('.page-header__categories a::text, .category a::text').getall()
        for category in categories:
            if category and any(keyword in category.lower() for keyword in ['character', 'people', 'individual']):
                # Extraire le type depuis le nom de catégorie
                if 'character' in category.lower():
                    type_from_category = category.replace('characters', '').replace('character', '').strip()
                    if type_from_category and len(type_from_category) > 1:
                        self.logger.info(f"✅ Type extrait des catégories: {type_from_category}")
                        return type_from_category
        
        return None
    
    def extract_additional_attributes(self, response):
        """Extraire les attributs supplémentaires - Méthode adaptative universelle"""
        attributes = []
        
        # ÉTAPE 1: Chercher dans différents types d'infobox
        infobox_selectors = [
            '.portable-infobox',
            '.infobox',
            'table.infobox',
            '.character-infobox', 
            '.info-box'
        ]
        
        for infobox_selector in infobox_selectors:
            infobox = response.css(infobox_selector)
            if not infobox:
                continue
            
            # Méthode 1: Structure portable-infobox moderne
            if 'portable-infobox' in infobox_selector:
                data_items = infobox.css('.pi-data')
                for item in data_items:
                    label = item.css('.pi-data-label::text').get()
                    value_elem = item.css('.pi-data-value')
                    
                    # Extraire valeur (texte ou liens)
                    value = value_elem.css('::text').get()
                    if not value:
                        value = value_elem.css('a::text').get()
                    
                    if label and value and self.is_useful_attribute(label.strip()):
                        attributes.append({
                            'name': self.clean_attribute_name(label.strip()),
                            'value': self.clean_attribute_value(value.strip())
                        })
            
            # Méthode 2: Structure table traditionnelle
            else:
                rows = infobox.css('tr')
                for row in rows:
                    # Chercher th/td ou td/td
                    cells = row.css('th, td')
                    if len(cells) >= 2:
                        label_elem = cells[0]
                        value_elem = cells[1]
                        
                        label = label_elem.css('::text').get()
                        value = value_elem.css('::text').get()
                        if not value:
                            value = value_elem.css('a::text').get()
                        
                        if label and value and self.is_useful_attribute(label.strip()):
                            attributes.append({
                                'name': self.clean_attribute_name(label.strip()),
                                'value': self.clean_attribute_value(value.strip())
                            })
            
            # Si on a trouvé des attributs, on arrête
            if attributes:
                break
        
        # ÉTAPE 2: Si pas d'infobox, chercher dans les listes de propriétés
        if not attributes:
            property_lists = response.css('dl, ul.properties, .character-stats')
            for prop_list in property_lists:
                dt_elements = prop_list.css('dt, li')
                for dt in dt_elements:
                    label = dt.css('::text').get()
                    value = dt.css('+ dd ::text, span.value::text').get()
                    
                    if label and value and self.is_useful_attribute(label.strip()):
                        attributes.append({
                            'name': self.clean_attribute_name(label.strip()),
                            'value': self.clean_attribute_value(value.strip())
                        })
        
        # ÉTAPE 3: Prioriser et retourner les meilleurs attributs
        prioritized_attributes = self.prioritize_attributes(attributes)
        
        result = {
            'attr1_name': 'Attribut 1',
            'attr1_value': 'Non spécifié',
            'attr2_name': 'Attribut 2', 
            'attr2_value': 'Non spécifié'
        }
        
        if len(prioritized_attributes) > 0:
            result['attr1_name'] = prioritized_attributes[0]['name']
            result['attr1_value'] = prioritized_attributes[0]['value']
            self.logger.info(f"✅ Attribut 1: {result['attr1_name']} = {result['attr1_value']}")
        
        if len(prioritized_attributes) > 1:
            result['attr2_name'] = prioritized_attributes[1]['name']
            result['attr2_value'] = prioritized_attributes[1]['value']
            self.logger.info(f"✅ Attribut 2: {result['attr2_name']} = {result['attr2_value']}")
        
        return result
    
    def is_useful_attribute(self, label):
        """Déterminer si un attribut est utile à extraire"""
        if not label or len(label.strip()) < 2:
            return False
        
        label_lower = label.lower().strip()
        
        # Exclure les champs basiques déjà extraits
        excluded_fields = [
            'name', 'nom', 'title', 'titre', 'species', 'espèce', 'gender', 'genre', 'sex', 'sexe'
        ]
        
        # Exclure les champs techniques
        technical_fields = [
            'image', 'photo', 'picture', 'file', 'template', 'category', 'edit', 'source'
        ]
        
        all_excluded = excluded_fields + technical_fields
        
        return not any(excluded in label_lower for excluded in all_excluded)
    
    def clean_attribute_name(self, name):
        """Nettoyer le nom d'un attribut"""
        import re
        # Supprimer les caractères de formatage
        cleaned = re.sub(r'[\n\t\r]', ' ', name)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip(':').strip()
        return cleaned
    
    def clean_attribute_value(self, value):
        """Nettoyer la valeur d'un attribut"""
        import re
        # Supprimer les caractères de formatage
        cleaned = re.sub(r'[\n\t\r]', ' ', value)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        return cleaned
    
    def prioritize_attributes(self, attributes):
        """Prioriser les attributs les plus intéressants"""
        if not attributes:
            return []
        
        # Mots-clés qui indiquent des attributs importants
        priority_keywords = [
            'power', 'ability', 'skill', 'talent', 'magic', 'element',
            'weapon', 'armor', 'equipment', 'tool',
            'affiliation', 'faction', 'team', 'group', 'organization',
            'rank', 'title', 'status', 'role', 'position',
            'origin', 'birthplace', 'nationality', 'home',
            'family', 'relative', 'relation', 'friend', 'enemy',
            
            # Français
            'pouvoir', 'compétence', 'magie', 'élément',
            'arme', 'armure', 'équipement', 'outil',
            'affiliation', 'équipe', 'groupe', 'organisation',
            'rang', 'titre', 'statut', 'rôle', 'position',
            'origine', 'nationalité', 'maison',
            'famille', 'parent', 'ami', 'ennemi'
        ]
        
        # Calculer un score de priorité pour chaque attribut
        scored_attributes = []
        for attr in attributes:
            score = 0
            name_lower = attr['name'].lower()
            
            # Bonus pour les mots-clés prioritaires
            for keyword in priority_keywords:
                if keyword in name_lower:
                    score += 2
            
            # Bonus pour les valeurs non-vides et interessantes
            if attr['value'] and len(attr['value']) > 2:
                score += 1
            
            # Malus pour les valeurs génériques
            generic_values = ['unknown', 'none', 'n/a', 'inconnu', 'aucun']
            if any(generic in attr['value'].lower() for generic in generic_values):
                score -= 1
            
            scored_attributes.append((score, attr))
        
        # Trier par score décroissant et retourner les meilleurs
        scored_attributes.sort(key=lambda x: x[0], reverse=True)
        return [attr for score, attr in scored_attributes[:5]]  # Max 5 meilleurs
    
    def closed(self, reason):
        """Générer le rapport à la fin du scraping"""
        self.stats['end_time'] = datetime.now()
        self.stats['duree_totale'] = str(self.stats['end_time'] - self.stats['start_time'])
        
        # Sauvegarder le rapport
        report_file = os.path.join(self.report_dir, f'rapport_{self.fandom_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"Scraping terminé. Rapport sauvegardé: {report_file}")
        self.logger.info(f"Personnages trouvés: {self.stats['personnages_trouves']}")
        self.logger.info(f"Pages traitées: {self.stats['pages_traitees']}")
        self.logger.info(f"Erreurs: {len(self.stats['erreurs'])}")