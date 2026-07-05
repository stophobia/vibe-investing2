import { createServer } from "./server.js";
import { config } from "./config.js";

const app = createServer();
app.listen(config.port, () => {
  console.log(`toss-qlib-middleware listening on :${config.port}`);
});
