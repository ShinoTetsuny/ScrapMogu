import express from 'express';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';
import dotenv from 'dotenv';
dotenv.config();
const app = express();
app.use(cors());
app.use(express.urlencoded({ extended: true }));
app.use((req, res, next) => {
    console.log(`[${new Date().toLocaleTimeString()}] ${req.method} ${req.url}`);
    next();
  });

  
const service = {
    scrap : `http://localhost:${process.env.PORT_SCRAP}`,
}

app.use("/api/:service", (req, res, next) => {
    const serviceName = req.params.service;
    const target = service[serviceName];
  
    if (target) {
      createProxyMiddleware({
        target,
        changeOrigin: true,
        pathRewrite: {
          [`^/api/${serviceName}`]: "",
        },
        logLevel: "debug",
      })(req, res, next);
    } else {
      res.status(502).send(`Service ${serviceName} non disponible.`);
    }
  });
  

export default app;