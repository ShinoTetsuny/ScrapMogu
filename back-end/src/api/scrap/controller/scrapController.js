import runScrapy from "../../../../utils/runScrapy.js";
import fs from "fs";

class ScrapController {
  constructor(data) {
    this.data = data;
  }

  async get_scrap_url(req, res) {
    try {
      this.data = req.body.url;

      await runScrapy(this.data);

      // 🔥 Chemin ABSOLU ici
      const filePath = "C:/Users/FabienETHEVE/OneDrive - ARTIMON/Bureau/MoguScrap/ScrapMogu/Mogu2/output.json";
      const data = await this.readJsonFile(filePath);

      return res.status(200).json({ data });
    } catch (error) {
      console.error(error);
      return res.status(500).json({ error: "An error occurred while processing the request" });
    }
  }

  async readJsonFile(filepath) {
    try {
      const data = fs.readFileSync(filepath, 'utf8');
      console.log(`Reading JSON file at ${filepath}`);
      return JSON.parse(data); // Attention ici si le fichier est mal formé
    } catch (error) {
      console.error(`Error reading JSON file at ${filepath}:`, error);
      throw error;
    }
  }
}

export default new ScrapController({});
