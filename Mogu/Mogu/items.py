# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FandomAnalysisItem(scrapy.Item):
    """Item pour l'analyse des fandoms et détection des pages de personnages"""
    fandom_name = scrapy.Field()
    fandom_url = scrapy.Field()
    characters_page_found = scrapy.Field()
    characters_page_url = scrapy.Field()
    characters_count = scrapy.Field()
    error_message = scrapy.Field()
    analysis_timestamp = scrapy.Field()


class CharacterItem(scrapy.Item):
    """Item pour stocker les informations des personnages/caractères"""
    # Informations de base (obligatoires)
    name = scrapy.Field()
    image_url = scrapy.Field()
    description = scrapy.Field()
    
    # Informations contextuelles
    fandom_name = scrapy.Field()
    fandom_url = scrapy.Field()
    character_url = scrapy.Field()
    
    # Attributs variables selon le fandom
    type_role_class = scrapy.Field()  # Type/Rôle/Classe/Origine
    attribute_1 = scrapy.Field()      # Premier attribut structuré
    attribute_2 = scrapy.Field()      # Deuxième attribut structuré
    
    # Métadonnées de scraping
    scraping_timestamp = scrapy.Field()
    scraping_success = scrapy.Field()
