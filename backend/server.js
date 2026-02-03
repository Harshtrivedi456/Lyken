import express from "express";

const app = express();
const PORT = 5000;

// middleware
app.use(express.json());

// ✅ ROOT ROUTE (THIS FIXES "Cannot GET /")
app.get("/", (req, res) => {
  res.send("Backend API is running 🚀");
});

// test API
app.get("/api/health", (req, res) => {
  res.json({ status: "OK", server: "up" });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
