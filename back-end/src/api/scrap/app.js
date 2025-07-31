import express from "express";

const appScrap = express();
appScrap.use(express.json());
appScrap.use(express.urlencoded({ extended: true }));

export default appScrap;