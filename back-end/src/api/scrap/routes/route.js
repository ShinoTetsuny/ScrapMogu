import express from "express";
const router = express.Router();
import scrapController from "../controller/scrapController.js";


router.post('/', (req, res) => { scrapController.get_scrap_url(req, res); });
router.get('/history', (req, res) => { scrapController.get_history_scrap(req, res); });
export default router;