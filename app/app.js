
const express = require("express");
const client = require("prom-client");

const app = express();
const PORT = 3000;

const register = new client.Registry();

client.collectDefaultMetrics({ register });

const requests = new client.Counter({
  name: "http_requests_total",
  help: "Total HTTP requests received",
  labelNames: ["method", "route", "status"],
  registers: [register]
});

const duration = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "HTTP request duration in seconds",
  labelNames: ["method", "route"],
  registers: [register]
});

app.use((req, res, next) => {
  const start = process.hrtime.bigint();

  res.on("finish", () => {
    const route = req.route?.path || req.path;

    requests.inc({
      method: req.method,
      route,
      status: String(res.statusCode)
    });

    duration.observe(
      { method: req.method, route },
      Number(process.hrtime.bigint() - start) / 1e9
    );
   
    console.log(
      JSON.stringify({
         timestamp: new Date().toISOString(),
         level: "info",
         message: "HTTP request completed",
         method: req.method,
         path: req.originalUrl,
         status: res.statusCode,
         duration_ms: Number(process.hrtime.bigint() - start) / 1e6
       })
     );
  });

  next();
});

app.get("/", (req, res) => {
  res.json({
    message: "Self-Healing Observability Demo",
    status: "healthy"
  });
});

app.get("/health", (req, res) => {
  res.json({ status: "healthy" });
});

app.get("/metrics", async (req, res) => {
  res.set("Content-Type", register.contentType);
  res.end(await register.metrics());
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Application listening on port ${PORT}`);
});
