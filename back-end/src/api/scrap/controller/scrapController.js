import runScrapy from "../../../../utils/runScrapy.js";
import fs from "fs";

class ScrapController {
  constructor(data) {
    this.data = data;
  }

  async get_scrap_url(req, res) {
    try {
      this.data = req.body.url;

      const filePath = "C:/Users/FabienETHEVE/OneDrive - ARTIMON/Bureau/MoguScrap/ScrapMogu/Mogu2/output.json";

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
