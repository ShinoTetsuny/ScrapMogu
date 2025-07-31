import app from "./src/api/gateway/app.js";
import appScrap from "./src/api/scrap/app.js";
import dotenv from "dotenv";
dotenv.config();

app.listen(process.env.PORT_GATEWAY, () => {
  console.log(`Gateway is running on port ${process.env.PORT_GATEWAY}`);
});

appScrap.listen(process.env.PORT_SCRAP, () => {
  console.log(`Scrap service is running on port ${process.env.PORT_SCRAP}`);
});