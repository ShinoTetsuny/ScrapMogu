import express from "express";
import scrap from "./routes/route.js"
const appScrap = express();
appScrap.use(express.json());
appScrap.use(express.urlencoded({ extended: true }));

appScrap.use("/scrap", scrap);

export default appScrap;