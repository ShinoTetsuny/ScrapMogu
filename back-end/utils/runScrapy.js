import { exec } from "child_process";
import path from "path";
import os from "os";

export default function runScrapy(url) {
  const projectDir = path.resolve("../Mogu");
  const isWindows = os.platform() === "win32";
  const scrapyExecutable = isWindows
    ? path.join(projectDir, ".venv", "Scripts", "scrapy.exe")
    : path.join(projectDir, ".venv", "bin", "scrapy");

  // <-- Changement ici : passer fandom_url au lieu de url
  const cmd = `"${scrapyExecutable}" crawl single_fandom_extractor -a fandom_url=${url} -o output.json`;

  return new Promise((resolve, reject) => {
    exec(cmd, { cwd: projectDir }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Erreur lors de l'exécution de Scrapy: ${error.message}`);
        return reject(error);
      }
      if (stderr) {
        console.error(`Erreur standard: ${stderr}`);
        return reject(new Error(stderr));
      }
      console.log(`Sortie standard: ${stdout}`);
      resolve(stdout);
    });
  });
}
