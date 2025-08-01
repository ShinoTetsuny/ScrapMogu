# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FandomCharacterItem(scrapy.Item):
    # Informations obligatoires
    name = scrapy.Field()                    # Nom du personnage
    image_url = scrapy.Field()              # URL de l'image principale (obligatoire)
    description = scrapy.Field()            # Description ou biographie
    character_type = scrapy.Field()         # Type / Rôle / Classe / Origine
    
    # 2 attributs structurés supplémentaires (variables selon l'univers)
    attribute1_name = scrapy.Field()        # Nom du 1er attribut (ex: "Pouvoir")
    attribute1_value = scrapy.Field()       # Valeur du 1er attribut (ex: "Télépathie")
    attribute2_name = scrapy.Field()        # Nom du 2e attribut (ex: "Affiliation")
    attribute2_value = scrapy.Field()       # Valeur du 2e attribut (ex: "Jedi")
    
    # Métadonnées
    source_url = scrapy.Field()             # URL de la page source
    fandom_name = scrapy.Field()            # Nom du fandom
    scraped_at = scrapy.Field()             # Timestamp du scraping
