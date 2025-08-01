# 🕷️ Scraper Universel Fandom

Scraper générique et intelligent capable de s'adapter automatiquement aux différentes structures HTML des wikis Fandom pour extraire les informations des personnages.

## 🎯 Fonctionnalités

- **Scraping universel** : S'adapte automatiquement aux différentes structures de wikis Fandom
- **Navigation intelligente** : Trouve automatiquement les catégories de personnages 
- **Extraction complète** : Récupère nom, image, description, type et attributs supplémentaires
- **Gestion d'erreurs** : Gère les pages manquantes, redirections, images inaccessibles
- **Rapports détaillés** : Génère des logs et statistiques complètes
- **Organisation des résultats** : Structure automatique des dossiers par fandom

## 📋 Données extraites

Pour chaque personnage :
- ✅ **Nom** (obligatoire)
- ✅ **Image principale** (URL, obligatoire) 
- ✅ **Description/Biographie**
- ✅ **Type/Rôle/Classe/Origine**
- ✅ **2 attributs supplémentaires** (pouvoirs, affiliation, etc.)

## 🚀 Installation

```bash
# Cloner le projet
cd Mogu2

# Installer les dépendances
pip install scrapy

# Optionnel: autres dépendances utiles
pip install requests beautifulsoup4
```

## 📖 Utilisation

### Méthode 1: Script de lancement (Recommandé)

```bash
# Scraper Star Wars
python run_scraper.py https://starwars.fandom.com/wiki/Main_Page

# Scraper Pokemon
python run_scraper.py https://pokemon.fandom.com/wiki/Pokemon_Wiki

# Scraper Marvel
python run_scraper.py https://marvel.fandom.com/wiki/Marvel_Database

# Avec options
python run_scraper.py https://naruto.fandom.com/wiki/Narutopedia --log-level DEBUG --delay 3.0
```

### Méthode 2: Commande Scrapy directe

```bash
# Depuis le dossier Mogu2/
scrapy crawl fandom_spider -a start_url=https://starwars.fandom.com/wiki/Main_Page
```

## 📁 Structure des résultats

```
ScrapMogu/
├── result/
│   └── [nom_fandom]/
│       └── [nom_fandom]_characters_20240101_120000.json
└── report/
    └── [nom_fandom]/
        └── rapport_[nom_fandom]_20240101_120000.json
```

### Format du fichier JSON de résultats

```json
{
  "fandom_name": "starwars",
  "scraped_at": "2024-01-01T12:00:00",
  "total_characters": 150,
  "characters": [
    {
      "name": "Luke Skywalker",
      "image_url": "https://static.wikia.nocookie.net/starwars/images/...",
      "description": "Luke Skywalker était un Jedi...",
      "character_type": "Jedi",
      "attribute1_name": "Affiliation", 
      "attribute1_value": "Alliance Rebelle",
      "attribute2_name": "Arme",
      "attribute2_value": "Sabre laser",
      "source_url": "https://starwars.fandom.com/wiki/Luke_Skywalker",
      "fandom_name": "starwars",
      "scraped_at": "2024-01-01T12:00:00"
    }
  ]
}
```

### Format du rapport

```json
{
  "pages_traitees": 200,
  "personnages_trouves": 150,
  "erreurs": [
    "Erreur lors du parsing de https://...: timeout"
  ],
  "pages_ignorees": [
    "https://starwars.fandom.com/wiki/PageSansImage"
  ],
  "start_time": "2024-01-01T12:00:00",
  "end_time": "2024-01-01T12:30:00", 
  "duree_totale": "0:30:00"
}
```

## 🔧 Configuration

Modifiez `Mogu2/settings.py` pour ajuster :

```python
# Délai entre requêtes (respecter les serveurs)
DOWNLOAD_DELAY = 2

# Nombre de tentatives en cas d'erreur
RETRY_TIMES = 3

# User agent
USER_AGENT = "Mogu2 Fandom Scraper (+https://github.com/...)"
```

## 🤖 Fonctionnement

Le scraper suit ce processus intelligent :

1. **Analyse de la page d'accueil** : Recherche les liens vers les catégories de personnages
2. **Navigation automatique** : Suit les liens de type `/wiki/Category:Characters`
3. **Exploration récursive** : Gère les sous-catégories automatiquement
4. **Extraction universelle** : S'adapte aux différentes structures HTML
5. **Validation** : Vérifie la présence obligatoire du nom et de l'image
6. **Sauvegarde organisée** : Classe les résultats par fandom avec timestamps

## 🐛 Gestion d'erreurs

Le scraper gère automatiquement :
- Pages inaccessibles ou supprimées
- Images manquantes ou inaccessibles  
- Structures HTML variables
- Timeouts et erreurs réseau
- Redirections
- Pages vides ou malformées

## 📊 Exemples de fandoms testés

- ⭐ Star Wars : `https://starwars.fandom.com/wiki/Main_Page`
- 🔥 Pokemon : `https://pokemon.fandom.com/wiki/Pokemon_Wiki`
- 🦸 Marvel : `https://marvel.fandom.com/wiki/Marvel_Database`
- 🏴‍☠️ One Piece : `https://onepiece.fandom.com/wiki/One_Piece_Wiki`
- 🧙 Harry Potter : `https://harrypotter.fandom.com/wiki/Main_Page`

## ⚠️ Limites et considérations

- **Respect des serveurs** : Délais configurés pour ne pas surcharger Fandom
- **Robots.txt** : Respecte automatiquement les règles robots.txt
- **Structures variables** : Certains fandoms peuvent nécessiter des ajustements
- **Images** : Seules les URLs d'images valides sont conservées
- **Taille** : Optimisé pour des fandoms de taille moyenne (< 1000 personnages)

## 🛠️ Personnalisation

Pour adapter le scraper à des structures HTML spécifiques, modifiez les méthodes dans `fandom_spider.py` :

- `extract_character_name()` : Sélecteurs pour le nom
- `extract_character_image()` : Sélecteurs pour l'image  
- `extract_character_description()` : Sélecteurs pour la description
- `extract_character_type()` : Sélecteurs pour le type
- `extract_additional_attributes()` : Sélecteurs pour les attributs

## 🚧 TODO

- [ ] Support des fandoms multi-langues
- [ ] Cache intelligent des images
- [ ] Interface web pour lancer les scraping
- [ ] Base de données pour stocker les résultats
- [ ] API REST pour interroger les données

## 📝 License

MIT License - Voir LICENSE pour plus de détails.