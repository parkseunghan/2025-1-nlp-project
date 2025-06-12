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
        const extracted =
            data.hybrid_results ||
            data.results ||
            data.llm_results ||
            data.symptoms; // ✅ FastAPI에서 반환하는 표준 키

        if (!Array.isArray(extracted)) {
            throw new Error("❌ 추출 결과가 배열 형식이 아닙니다.");
        }

        console.log("✅ 추출된 증상:", extracted);

        // ✅ 증상이 객체 배열이면 그대로 사용
        const symptoms = extracted.filter(item => typeof item === "object" && item.symptom);

        if (symptoms.length === 0) {
            return res.status(400).json({ error: "❌ 추출된 증상이 없습니다." });
        }

        // 2. 질병 예측 요청
        const predictRes = await fetch("http://localhost:8002/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symptoms }), // ✅ 객체 배열 전달
        });

        const prediction = await predictRes.json();

        res.json({
            symptoms, // ✅ 프론트로도 객체 배열 그대로 전달
            result: prediction.result || prediction,
        });
    } catch (err) {
        console.error("❌ 서버 오류:", err.message);
        res.status(500).json({ error: "예측 실패", message: err.message });
    }
}
app.post("/predict/nlp", async (req, res) => {
    const { text } = req.body;
    await extractAndPredict("http://localhost:8001/extract/nlp", text, res);
});

app.post("/predict/hybrid", async (req, res) => {
    const { text } = req.body;
    await extractAndPredict("http://localhost:8001/extract/hybrid", text, res);
});


app.post("/predict/llm", async (req, res) => {
    const { text } = req.body;
    await extractAndPredict("http://localhost:8001/extract/llm", text, res);
});

app.get("/logs/unknown-symptoms", async (req, res) => {
    try {
        const response = await fetch("http://localhost:8001/logs/unknown-symptoms");
        const data = await response.json();
        res.json(data);
    } catch (err) {
        console.error("❌ 로그 조회 실패:", err.message);
        res.status(500).json({ error: "로그 조회 실패", message: err.message });
    }
});


const PORT = 3000;
app.listen(PORT, () => {
    console.log(`✅ 예측 웹 서버 실행 중: http://localhost:${PORT}`);
});
