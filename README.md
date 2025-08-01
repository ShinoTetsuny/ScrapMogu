Notes : Malheuresement par manque de temps le front n'est pas opérationnel, la seul fonctionnalités qui manque c'est l'affichage des cartes des personnages. 

# Backend 

## Installation 
Ouvrez un terminal et placez-vous dans le dossier back-end :
` cd back-end `
### Installer les dépendances  
 Installez les dépendances : 
 ` npm install `

## Lancement du serveur 
Pour démarrer le serveur Express en mode dev : 
` npm run start `

## Lancement des tests 
Pour exécuter les tests unitaires avec Jest : 
` npm run test `

## Remarques 
. Assurez-vous de créer un fichier .env si le projet utilise des variables d'environnement.
. Les erreurs peuvent être journalisées dans la console au lancement pour faciliter le débogage.
. Assurez-vous de modifier les filepaths dans ScrapController.js de get_scrap_url afin de pointer vers le bon fichier, et celui du get_history_scrap

# Scrapy Mogu2

## Installation 
Ouvrez un terminal et placez-vous dans le dossier Mogu2, puis faites : 
` .venv/Scripts/Activate` afin de lancer le .venv
puis : 
` pip install scrapy `

# Front End

## Installation 
` npm install `

## Lancement du serveur 
`npm run dev`
