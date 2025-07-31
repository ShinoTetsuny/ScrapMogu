import fs from 'fs/promises';
import { statSync } from 'fs';
import generateResponse from '../src/api/scrap/utils/generateResponse.js';

const FICHIER = './data/data.json';

let lastModifiedTime = null;

async function checkFile() {
  try {
    const stats = statSync(FICHIER);
    const mtime = stats.mtime.getTime();

    if (lastModifiedTime === null) {
      lastModifiedTime = mtime;
      console.log(`[Init] Fichier détecté, dernière modif : ${stats.mtime}`);
      return;
    }

    if (mtime !== lastModifiedTime) {
      lastModifiedTime = mtime;
      console.log(`[Changement] Fichier modifié à : ${new Date(mtime).toLocaleString()}`);

      // Lire le contenu et générer la réponse
      const contenu = await fs.readFile(FICHIER, 'utf-8');
      const dataJson = JSON.parse(contenu);

      if (dataJson.url) {
        const reponse = await generateResponse(dataJson.url);
        console.log('Réponse générée:', reponse);

        // Ici tu peux sauvegarder la réponse, ou faire ce que tu veux avec
      } else {
        console.log('Pas d\'URL dans le fichier');
      }
    }
  } catch (err) {
    console.error('Erreur lors de la lecture du fichier:', err.message);
  }
}


export default checkFile;