import app from "./src/api/gateway/app.js";
import appScrap from "./src/api/scrap/app.js";
import dotenv from "dotenv";
import checkFile from "./utils/checker.js";
import { CronJob } from "cron";
dotenv.config();
// Lancer le cron job pour vérifier le fichier toutes les 5 secondes
const job = new CronJob('*/5 * * * * *', () => {
  console.log('Vérification du fichier toutes les 5 secondes...');
  checkFile();
});
job.start();
app.listen(process.env.PORT_GATEWAY, () => {
  console.log(`Gateway is running on port ${process.env.PORT_GATEWAY}`);
});

appScrap.listen(process.env.PORT_SCRAP, () => {
  console.log(`Scrap service is running on port ${process.env.PORT_SCRAP}`);
});