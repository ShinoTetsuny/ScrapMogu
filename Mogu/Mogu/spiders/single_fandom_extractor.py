import scrapy
from ..items import CharacterItem



class CharacterScraperSpider(scrapy.Spider):
    name = "character_scraper_2"

    def __init__(self, *args, **kwargs):
        super(CharacterScraperSpider, self).__init__(*args, **kwargs)
        self.characters_data = []

        self.fandom_url = kwargs.get('fandom_url')
        self.fandom_name = kwargs.get('fandom_name', 'Inconnu')

        if not self.fandom_url:
            raise ValueError("Le paramètre 'fandom_url' est requis pour lancer ce spider.")

    def start_requests(self):
        yield scrapy.Request(
            url=self.fandom_url,
            callback=self.parse_characters_page,
            meta={
                'fandom_name': self.fandom_name,
                'fandom_url': self.fandom_url
            }
        )

    def parse_characters_page(self, response):
        characters = response.css("table.article-table tr")[1:]

        for character in characters:
            name = character.css("td:nth-child(1)::text").get()
            role = character.css("td:nth-child(2)::text").get()
            description = character.css("td:nth-child(3)::text").get()
            image = character.css("td:nth-child(4) img::attr(src)").get()

            if name or role or description or image:
                item = CharacterItem(
                    nom=name.strip() if name else None,
                    role=role.strip() if role else None,
                    description=description.strip() if description else None,
                    image=image,
                    fandom=self.fandom_name,
                    source_url=response.meta['fandom_url']
                )
                yield item
