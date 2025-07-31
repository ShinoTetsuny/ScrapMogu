import generateResponse from "../utils/generateResponse.js";
import * as fs from "fs";
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
    const url_json = {
      url: this.data,
    };

    fs.writeFile('data/data.json', JSON.stringify(url_json), (err) => {
      if (err) {
        return res
          .status(500)
          .json({ error: "An error occurred while saving the URL" });
      }
      return res.status(200).json({
        message: "URL saved successfully",
      });
    });

  }
  async change_scrap_data(req, res) {
    try {
      this.data = req.body;
    } catch (error) {
      return res
        .status(500)
        .json({ error: "An error occurred while updating data" });
    }

    const resp = await generateResponse(this.data.text);
    if (!resp) {
      return res
        .status(500)
        .json({ error: "An error occurred while generating response" });
    }
    return res.status(200).json({ response: resp });
  }
}

export default new ScrapController({});
