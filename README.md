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

## Strucutres du projet 

back-end/
├───__test__
|
├───src
│   └───api
│       ├───gateway
│       └───scrap
│           ├───controller
│           ├───models
│           ├───routes
│           └───utils
│   
│
│
├── .env
|── server.js
├── package.json
└── README.md

## Remarques 
. Assurez-vous de créer un fichier .env si le projet utilise des variables d'environnement.
. Les erreurs peuvent être journalisées dans la console au lancement pour faciliter le débogage.