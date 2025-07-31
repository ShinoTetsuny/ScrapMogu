import runScrapy from "../../../../utils/runScrapy.js";

class ScrapController {
  constructor(data) {
    this.data = data;
  }
  async get_scrap_url(req, res) {
    try {
      this.data = req.body.url;
    } catch (error) {
      return res
        .status(500)
        .json({ error: "An error occurred while processing the request" });
    }
    
    runScrapy(this.data)
      .then((result) => {
        res.status(200).json({ result });
      })
      .catch((error) => {
        console.error(error);
        res.status(500).json({ error: "An error occurred while processing the request" });
      });
  }
}

export default new ScrapController({});
