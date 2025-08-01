import runScrapy from "../../../../utils/runScrapy.js";
import fs from "fs";
import path from "path";
class ScrapController {
  constructor(data) {
    this.data = data;
  }

  async get_scrap_url(req, res) {
    try {
      this.data = req.body.url;

      const filePath = "C:/Dev/WebScrapping/dayFour/ScrapMogu/Mogu2/output.json";

      // 🧹 Supprimer le fichier s'il existe
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        console.log("🗑️ Ancien fichier output.json supprimé.");
      }

      // 🔁 Lancement du scraping
      await runScrapy(this.data);

      // ✅ Vérification après scraping
      if (!fs.existsSync(filePath)) {
        console.error("❌ Fichier output.json non généré.");
        return res.status(404).json({ error: "Le fichier output.json est introuvable après scraping." });
      }

      const data = await this.readJsonFile(filePath);

      return res.status(200).json({ data });
    } catch (error) {
      console.error(error);
      return res.status(500).json({ error: "Une erreur est survenue lors du traitement." });
    }
  }

 async get_history_scrap(req, res) {
    try {
      const baseDir = "C:/Dev/WebScrapping/dayFour/ScrapMogu/result";

      // Récupérer la liste des dossiers dans result (catégories)
      const categories = fs.readdirSync(baseDir, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name);

      const history = [];

      for (const category of categories) {
        const categoryPath = path.join(baseDir, category);

        // Lister les fichiers JSON dans ce dossier catégorie
        const files = fs.readdirSync(categoryPath, { withFileTypes: true })
          .filter(dirent => dirent.isFile() && dirent.name.endsWith(".json"))
          .map(dirent => dirent.name);

        for (const file of files) {
          const filePath = path.join(categoryPath, file);

          try {
            const fileData = await this.readJsonFile(filePath);
            history.push({
              category,
              file,
              data: fileData
            });
          } catch (err) {
            console.error(`Erreur lecture fichier ${filePath}:`, err);
            // Tu peux choisir d’ignorer ou retourner une erreur selon ce que tu veux faire
          }
        }
      }

      return res.status(200).json({ history });
    } catch (error) {
      console.error("Erreur dans get_history_scrap:", error);
      return res.status(500).json({ error: "Erreur lors de la récupération de l'historique." });
    }
  }
  async readJsonFile(filepath) {
    try {
      const data = fs.readFileSync(filepath, 'utf8');
      console.log(`📖 Lecture du fichier JSON à : ${filepath}`);
      return JSON.parse(data);
    } catch (error) {
      console.error(`❌ Erreur lecture/parsing JSON :`, error);
      throw error;
    }
  }
}

export default new ScrapController({});
