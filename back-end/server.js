import app from "./src/api/gateway/app.js";
import dotenv from "dotenv";
dotenv.config();

app.listen(process.env.PORT_GATEWAY, () => {
  console.log(`Gateway is running on port ${process.env.PORT_GATEWAY}`);
});