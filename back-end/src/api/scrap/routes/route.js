import express from "express";
const router = express.Router();
import scrapController from "../controller/scrapController.js";


router.post("/",(req, res)=>{ scrapController.change_scrap_data(req, res); });

export default router;