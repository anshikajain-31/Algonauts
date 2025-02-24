require('dotenv').config();
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// ✅ Corrected MongoDB Connection
const MONGO_URI = process.env.MONGO_URI || "mongodb+srv://anshikajyotijain:Saloni%401234@cluster0.u5jtr.mongodb.net/news_database?retryWrites=true&w=majority&appName=Cluster0";

mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => {
        console.log("✅ MongoDB Connected to:", mongoose.connection.db.databaseName);
    })
    .catch(err => console.error("❌ MongoDB Connection Error:", err));

// ✅ Correct Schema & Model for `summaries` Collection
const newsSchema = new mongoose.Schema({
    title: String,
    summary: String,
    translated_summary: String,
    image: String,
    category: String
});
const News = mongoose.model('summaries', newsSchema);  // ✅ Uses the correct collection name

// ✅ Default Route
app.get('/', (req, res) => {
    res.send("Server is running! Use /news endpoint.");
});

// ✅ News API Route (Fetching from Correct Collection)
app.get('/news', async (req, res) => {
    try {
        const category = req.query.category || "all";

        // ✅ Case-insensitive category matching
        const query = category === "all" ? {} : { category: { $regex: `^${category}$`, $options: "i" } };

        console.log("🔍 Querying MongoDB with:", JSON.stringify(query));  // Debugging

        const newsList = await News.find(query, { _id: 0, title: 1, summary: 1, translated_summary: 1, image: 1, category: 1 });

        console.log("✅ Fetched News:", newsList);  // Debugging
        res.json(newsList);
    } catch (error) {
        console.error("❌ Error fetching news:", error);
        res.status(500).json({ error: "Server error" });
    }
});
const { createProxyMiddleware } = require('http-proxy-middleware');
app.use('/api', createProxyMiddleware({ 
    target: 'https://isegp27f20.execute-api.eu-north-1.amazonaws.com',
    changeOrigin: true
}));


// ✅ Start Server
app.listen(PORT, () => {
    console.log(`🚀 Server running at http://localhost:${PORT}`);
});
