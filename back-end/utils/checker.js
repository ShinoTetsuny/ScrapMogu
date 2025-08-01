import fs from 'fs/promises';
import { statSync, readdirSync } from 'fs';
import path from 'path';
import generateResponse from '../src/api/scrap/utils/generateResponse.js';

const DOSSIER = '../Mogu/data/';

let lastModifiedTime = null;

async function checkFilesInFolder() {
  try {
    const dossierStats = statSync(DOSSIER);
    const mtime = dossierStats.mtime.getTime();

    if (lastModifiedTime === null) {
      lastModifiedTime = mtime;
      console.log(`[Init] Dossier détecté, dernière modif : ${dossierStats.mtime}`);
      return;
    }

    if (mtime !== lastModifiedTime) {
      lastModifiedTime = mtime;
      console.log(`[Changement] Dossier modifié à : ${new Date(mtime).toLocaleString()}`);

      // Lire tous les fichiers du dossier
      const fichiers = readdirSync(DOSSIER);

      for (const nomFichier of fichiers) {
        const cheminFichier = path.join(DOSSIER, nomFichier);

        try {
          const contenu = await fs.readFile(cheminFichier, 'utf-8');
          const dataJson = JSON.parse(contenu);

          if (dataJson.url) {
            const reponse = await generateResponse(dataJson.url);
            console.log(`Réponse pour ${nomFichier} :`, reponse);

            // Tu peux aussi écrire la réponse dans un autre fichier, par exemple :
            // await fs.writeFile(`${DOSSIER}/response_${nomFichier}`, JSON.stringify(reponse, null, 2));
          } else {
            console.log(`Pas d'URL dans ${nomFichier}`);
          }
        } catch (err) {
          console.error(`Erreur avec le fichier ${nomFichier} :`, err.message);
        }
      }
    }
  } catch (err) {
    console.error('Erreur dans la vérification du dossier :', err.message);
  }
}

export default checkFilesInFolder;
