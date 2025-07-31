import { exec } from "child_process";
import path from "path";
import os from "os";

export default function runScrapy(url) {
  const projectDir = path.resolve("../Mogu");
  const isWindows = os.platform() === "win32";
  const scrapyExecutable = isWindows
    ? path.join(projectDir, ".venv", "Scripts", "scrapy.exe")
    : path.join(projectDir, ".venv", "bin", "scrapy");

  // Nettoyage du chemin (important sur Windows)
  const scrapyCmd = isWindows
    ? `"${scrapyExecutable.replace(/\\/g, "/")}"`
    : `"${scrapyExecutable}"`;

  const cmd = `"${scrapyExecutable}" crawl character_scraper_2 -a fandom_url=${url} -o output.json`;



  return new Promise((resolve, reject) => {
    exec(cmd, { cwd: projectDir }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Erreur d'exécution Scrapy: ${error.message}`);
        return reject(error);
      }
      if (stderr) {
        console.warn(`Scrapy stderr: ${stderr}`);
      }
      console.log(`Scrapy stdout: ${stdout}`);
      resolve(stdout);
    });
  });
}
