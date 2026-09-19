import { NextResponse } from "next/server";
import Groq from "groq-sdk";
import { GoogleGenerativeAI } from "@google/generative-ai";

export async function POST(req: Request) {
  try {
    const { text } = await req.json();

    if (!text) {
      return NextResponse.json({ error: "Text is required" }, { status: 400 });
    }

    const groqKey = process.env.GROQ_API_KEY;
    const geminiKey = process.env.GEMINI_API_KEY;

    const prompt = `
You are an expert UX researcher classifying failure stages in a photo retrieval engine for Google Photos.
Analyze the following user feedback and extract the failure taxonomy.

User Feedback: "${text}"

Output strictly as a valid JSON object with EXACTLY these keys:
{
  "failure_stage": "Short categorical string (e.g., Face Recognition & Pet Grouping Errors, Date & Timeline Desynchronization, Search Retrieval Failure, Ask Photos / Gemini AI Regressions, Document & Receipt Text Inaccuracies)",
  "evidence_quote": "The exact substring from the text that proves this failure",
  "workaround_attempted": true or false,
  "resolved": true or false,
  "severity": number from 1 (minor annoyance) to 5 (complete blocker),
  "user_intent": "What were they actually trying to find?"
}
`;

    let cleanJson = "";

    // Strategy 1: Try Groq first (fast, reliable, generous free tier limits)
    if (groqKey) {
      const preferredModel = process.env.LLM_AGREEMENT_MODEL || "groq/compound-mini";
      const candidateModels = [preferredModel, "groq/compound-mini", "qwen/qwen3.8-27b"];
      const groq = new Groq({ apiKey: groqKey });

      for (const modelName of candidateModels) {
        try {
          const completion = await groq.chat.completions.create({
            messages: [
              { role: "system", content: "You are a JSON-only response engine. Return strictly raw JSON." },
              { role: "user", content: prompt }
            ],
            model: modelName,
            temperature: 0.1,
            max_tokens: 512,
            response_format: { type: "json_object" }
          });

          cleanJson = completion.choices[0]?.message?.content || "";
          if (cleanJson) break;
        } catch (e: any) {
          console.warn(`Groq analyze with ${modelName} failed:`, e?.message);
        }
      }
    }

    // Strategy 2: Fallback to Gemini if Groq was not available
    if (!cleanJson && geminiKey) {
      try {
        const genAI = new GoogleGenerativeAI(geminiKey);
        const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
        const result = await model.generateContent(prompt);
        const response = await result.response;
        cleanJson = response.text().replace(/```json\n?/, "").replace(/```\n?$/, "").trim();
      } catch (geminiErr: any) {
        console.error("Gemini analyze fallback also failed:", geminiErr?.message);
      }
    }

    if (!cleanJson) {
      throw new Error("All AI classification models are currently unavailable. Please try again shortly.");
    }

    let parsedData = {};
    try {
      parsedData = JSON.parse(cleanJson);
    } catch (e) {
      parsedData = { raw_output: cleanJson };
    }

    return NextResponse.json(parsedData);
  } catch (error: any) {
    console.error("Analyze API Error:", error);
    return NextResponse.json({ error: error.message || "Failed to analyze" }, { status: 500 });
  }
}
