import { NextResponse } from "next/server";
import Groq from "groq-sdk";
import { GoogleGenerativeAI } from "@google/generative-ai";

// In-memory cache
const queryCache = new Map<string, string>();

export async function POST(req: Request) {
  try {
    const { query, stream = false } = await req.json();

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    const cleanStr = (s: string) =>
      s
        .replace(/\b(\d+)\s+items\b/gi, "$1 reviews")
        .replace(/\bitems\b/gi, "reviews")
        .replace(/\bitem\b/gi, "review");

    const cacheKey = query.trim().toLowerCase();

    // Check cache first to save quota
    if (queryCache.has(cacheKey)) {
      const cleanCached = cleanStr(queryCache.get(cacheKey) || "");

      if (stream) {
        const encoder = new TextEncoder();
        const customReadable = new ReadableStream({
          async start(controller) {
            // Stream cached tokens quickly for fluid typing effect
            const words = cleanCached.split(" ");
            for (let i = 0; i < words.length; i++) {
              const word = words[i] + (i < words.length - 1 ? " " : "");
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text: word })}\n\n`));
              await new Promise((r) => setTimeout(r, 15));
            }
            controller.enqueue(encoder.encode("data: [DONE]\n\n"));
            controller.close();
          },
        });

        return new Response(customReadable, {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
          },
        });
      }

      return NextResponse.json({
        query: query,
        content: cleanCached,
        metrics: [],
        cached: true,
      });
    }

    const contextData = `
VERIFIED DATASET CONTEXT (4,615 public user reviews analyzed from Google Play Store, Apple App Store, and Google Photos Community; 0 from YouTube):

OVERALL METRICS:
• Total analyzed reviews: 4,615
• Unresolved search failures: 4,364 reviews (94.6%)
• Found after workaround: 251 reviews (5.4%)
• Sources: Google Play Store (3,018 reviews, 65.4%), Apple App Store (1,546 reviews, 33.5%), Google Photos Community (51 discussions, 1.1%).

TOP 14 FAILURE CLUSTERS (RANKED BY OPPORTUNITY SCORE = Freq x Severity x Recency x Unresolved):
1. Vague Memory & Natural Language Breakdown: Score 83.0 (1,197 reviews, 25.9%, 95.1% unresolved)
2. Date & Timeline Desynchronization: Score 52.9 (829 reviews, 18.0%, 94.2% unresolved)
3. Face Recognition & Pet Grouping Errors: Score 34.7 (634 reviews, 13.7%, 93.8% unresolved)
4. Ask Photos / Gemini AI Regressions: Score 17.4 (276 reviews, 6.0%, 96.4% unresolved)
5. Document, Receipt & Text (OCR) Inaccuracies: Score 16.2 (309 reviews, 6.7%, 95.5% unresolved)
6. Hidden & Archived Folder Search Blindness: Score 14.8 (272 reviews, 5.9%, 96.0% unresolved)
7. Search Retrieval Failure: Zero Results: Score 12.9 (235 reviews, 5.1%, 95.7% unresolved)
8. Album vs. Main Library Disconnection: Score 12.1 (227 reviews, 4.9%, 94.7% unresolved)
9. Search Query Visual Clutter: Memes & Screenshots: Score 10.4 (198 reviews, 4.3%, 94.9% unresolved)
10. Inability to Refine / Multi-Condition Queries: Score 10.1 (195 reviews, 4.2%, 93.8% unresolved)
11. Video Content & In-Video Action Search: Score 9.2 (173 reviews, 3.7%, 95.4% unresolved)
12. Missing Location & Geotag Failures: Score 2.8 (54 reviews, 1.2%, 94.4% unresolved)
13. Offline / Flight Mode Search Inaccessibility: Score 0.7 (14 reviews, 0.3%, 92.9% unresolved)
14. Duplicate & Burst Photo Flooding: Score 0.1 (2 reviews, <0.1%, 100% unresolved)

KINDS OF OLD PHOTOS USERS STRUGGLE TO RETRIEVE:
• Everyday Visual Moments (1,756 reviews, 38.0%)
• Documents & Receipts (OCR) (975 reviews, 21.1%)
• Pets & Animals (916 reviews, 19.8%)
• Screenshots & Clutter (475 reviews, 10.3%)
• Family & Children (458 reviews, 9.9%)
• Travel & Vacations (251 reviews, 5.4%)
• Videos & Clips (173 reviews, 3.7%)
• Milestone Events (122 reviews, 2.6%)
• Old Scanned & Heritage Prints (98 reviews, 2.1%)

WHAT PEOPLE ACTUALLY REMEMBER ABOUT A PHOTO:
• Visual Appearance & Objects (e.g. red dress, car, dog with hat) (2,048 reviews, 44.4%)
• Vague Visual Memory / Scene Impression (1,938 reviews, 42.0%)
• Person / Face (e.g. daughter, mom, friend) (787 reviews, 17.1%)
• Place / Setting (e.g. beach, cafe in Goa, school) (523 reviews, 11.3%)
• Text in Image / Key Words (e.g. medicine name, receipt) (397 reviews, 8.6%)
• Approximate Time / Season (e.g. summer 2021, two years ago) (227 reviews, 4.9%)
• Event / Occasion (e.g. wedding, party) (70 reviews, 1.5%)

WHAT INFORMATION PEOPLE HAVE FORGOTTEN:
• Exact Calendar Date & Geographic Context (4,090 reviews, 88.6%)
• Specific Album / Folder Name (475 reviews, 10.3%)
• Precise Search Keywords / Filename (45 reviews, 1.0%)
• Exact Calendar Date (8 reviews, 0.2%)
• Exact Geotag / GPS (1 review, <0.1%)

HOW USERS FORMULATE SEARCHES WHEN MEMORY IS INCOMPLETE:
• Exploratory Natural Language Phrasing (describing visual cues in conversational sentences) (2,421 reviews, 52.5%)
• Ask Photos / Gemini Conversational Queries (1,383 reviews, 30.0%)
• Browsing Albums & Folders Manually (376 reviews, 8.1%)
• Applying Structured Search Filters (272 reviews, 5.9%)
• Single Keyword Searches (74 reviews, 1.6%)
• Manual Chronological Timeline Scrolling (49 reviews, 1.1%)
• Giving Up / Abandoning Search (40 reviews, 0.9%)

TOP WORKAROUNDS (251 reviews reporting workarounds):
• Exporting / Switching to 3rd-party gallery apps (137 reviews, 54.6%)
• Endless manual timeline scrolling (76 reviews, 30.3%)
• Relying on pre-made Albums / Favorites (26 reviews, 10.4%)
• Disabling Gemini AI / reverting to classic search (7 reviews, 2.8%)
• Searching Trash / Locked Folder manually (5 reviews, 2.0%)

QUALITY AUDIT & MODEL AGREEMENT NUMBERS:
• 100-item stratified audit: 92.0% Precision, 89.4% Estimated Recall, 90.7% F1 Score.
• 300-item inter-model agreement (Gemini 2.5 Flash vs Groq LLaMA): 93.3% Relevance Agreement, 87.0% Failure Stage Agreement (Cohen's Kappa = 0.84).
`;

    const systemPrompt = `You are the Google Photos AI Discovery Engine assistant.
You analyze 4,615 verified user reviews from Google Play Store, Apple App Store, and Google Photos Community (0 from YouTube).

CRITICAL VOCABULARY & RULES:
1. NEVER use the word "items". Always use "reviews", "users", or "cases" (e.g., "(1,197 reviews, 25.9%)").
2. Answer ANY evaluator question accurately using ONLY the verified dataset numbers above.
3. Keep responses direct, crisp, and data-backed (typically 50-90 words).
4. If comparing two categories (e.g. screenshots vs travel, or OCR vs vague memory), provide the exact numbers for each and a 1-sentence PM takeaway.
5. If asked about competitors or topics unrelated to Google Photos retrieval, politely decline: "This discovery engine is strictly scoped to Google Photos retrieval feedback."
6. NEVER fabricate or guess statistics.

${contextData}`;

    const groqKey = process.env.GROQ_API_KEY;
    const geminiKey = process.env.GEMINI_API_KEY;

    // Handle streaming response
    if (stream) {
      const encoder = new TextEncoder();

      // Attempt streaming with Groq
      if (groqKey) {
        try {
          const groq = new Groq({ apiKey: groqKey });
          const streamCompletion = await groq.chat.completions.create({
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user", content: query },
            ],
            model: "groq/compound-mini",
            temperature: 0.1,
            max_tokens: 300,
            stream: true,
          });

          let fullAccumulated = "";

          const readable = new ReadableStream({
            async start(controller) {
              try {
                for await (const chunk of streamCompletion) {
                  const content = chunk.choices[0]?.delta?.content || "";
                  if (content) {
                    const clean = cleanStr(content);
                    fullAccumulated += clean;
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text: clean })}\n\n`));
                  }
                }

                // Cache complete answer
                if (fullAccumulated.trim()) {
                  queryCache.set(cacheKey, fullAccumulated.trim());
                }

                controller.enqueue(encoder.encode("data: [DONE]\n\n"));
                controller.close();
              } catch (streamErr) {
                controller.error(streamErr);
              }
            },
          });

          return new Response(readable, {
            headers: {
              "Content-Type": "text/event-stream",
              "Cache-Control": "no-cache",
              Connection: "keep-alive",
            },
          });
        } catch (groqStreamErr) {
          console.warn("Groq streaming failed, falling back to non-streaming or Gemini:", groqStreamErr);
        }
      }
    }

    // Non-streaming fallback
    let textOutput = "";
    if (groqKey) {
      try {
        const groq = new Groq({ apiKey: groqKey });
        const completion = await groq.chat.completions.create({
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: query },
          ],
          model: "groq/compound-mini",
          temperature: 0.1,
          max_tokens: 300,
        });
        textOutput = completion.choices[0]?.message?.content || "";
      } catch (err) {
        console.warn("Groq standard query failed:", err);
      }
    }

    if (!textOutput && geminiKey) {
      try {
        const genAI = new GoogleGenerativeAI(geminiKey);
        const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
        const result = await model.generateContent(`${systemPrompt}\n\nUser Question: ${query}`);
        const response = await result.response;
        textOutput = response.text();
      } catch (geminiErr) {
        console.error("Gemini query failed:", geminiErr);
      }
    }

    if (!textOutput) {
      throw new Error("Unable to contact AI model providers.");
    }

    const cleanedFinal = cleanStr(textOutput.trim());
    queryCache.set(cacheKey, cleanedFinal);

    return NextResponse.json({
      query: query,
      content: cleanedFinal,
      metrics: [],
      cached: false,
    });
  } catch (error: any) {
    console.error("Query API Error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to answer query" },
      { status: 500 }
    );
  }
}
