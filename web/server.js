const express = require("express");
const fetch = require("node-fetch"); // npm install node-fetch@2
const path = require("path");

const app = express();
app.use(express.json());
app.use(express.static("public"));

async function extractAndPredict(endpoint, text, res) {
    try {
        // 1. 증상 추출 요청
        const extractRes = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        const data = await extractRes.json();
        const extracted = data.hybrid_results || data.results || data.llm_results;

        if (!Array.isArray(extracted)) {
            throw new Error("❌ 추출 결과가 배열 형식이 아닙니다.");
        }


        const symptoms = extracted
            .map((item) => item.symptom)
            .filter(Boolean); // null/undefined 제거

        if (symptoms.length === 0) {
            return res.status(400).json({ error: "❌ 추출된 증상이 없습니다." });
        }

        // 2. 질병 예측 요청
        const predictRes = await fetch("http://localhost:8002/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symptoms }),
        });

        const prediction = await predictRes.json();

        res.json({
            symptoms,
            result: prediction.result || prediction, // fallback 처리
        });
    } catch (err) {
        console.error("❌ 서버 오류:", err.message);
        res.status(500).json({ error: "예측 실패", message: err.message });
    }
}

app.post("/predict", async (req, res) => {
    const { text } = req.body;
    await extractAndPredict("http://localhost:8001/extract/hybrid", text, res);
});

app.post("/predict2", async (req, res) => {
    const { text } = req.body;
    await extractAndPredict("http://localhost:8001/extract", text, res);
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`✅ 예측 웹 서버 실행 중: http://localhost:${PORT}`);
});
