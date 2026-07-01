# ai201-project4-provenance-guard



\## Architecture Overview

(Architecture overview: the path a submission takes from input to transparency label).



POST /submit (text, creator\_id)

|

|

v

Signal 1: Groq LLM Score

Signal 2: Stylometric Heuristics

|

|

v

Combined Confidence Score

(0.6 × Groq) + (0.4 × Stylometric)

|

|

v

Transparency Label (based on score range)

|

|

v

JSON Response (content\_id, attribution, scores, label)





\## Detection Signals

\*\*Signal 1 — Groq (LLM-based classification)\*\*

&#x09;- Send the text to Groq with prompt "rate how likely this was written by AI, 0-1" then parse the number back. Selected this because it captures semantic and stylistic coherence holistically.

&#x09;- Blind spot: possible to be fooled by AI text slightly altered or by human written text with polished grammar/punctuation.



\*\*Signal 2 — Stylometric heuristics\*\*

&#x09;- Sentence length variance — length of sentence produced by humans will vary more. AI will tend to have a more uniform sentence length.

&#x09;- Type-token ratio (vocabulary diversity) — the ratio of unique words compared to total words; AI will often reuse the same vocabulary more than human text.

&#x20;	- Blind spot: hard to find variance in text short in length. Structured texts like poetry may be repetitive in words and length, which can be a false positive for an AI flag.





\## Confidence Scoring

Signals are combined via: combined\_score = (0.6 × groq\_score) + (0.4 × stylometric\_score)



\*\*Score ranges map to three categories:\*\*

\- 0.0–0.39 → Likely human-written

\- 0.4–0.69 → Uncertain

\- 0.7–1.0 → Likely AI-generated



\*\*Example 1:\*\*

``` text

Text: "Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment



Results:   

&#x20; "attribution": "uncertain",

&#x20; "confidence": 0.585,

&#x20; "content\_id": "0557f3da-bc6a-448d-9dd4-c601334d388f",

&#x20; "creator\_id": "test-user-2",

&#x20; "groq\_score": 0.8,

&#x20; "label": "The system is not confident about authorship. May be AI-generated, human-generated, or both (could be AI text slightly altered by a human).",

&#x20; "stylometric\_score": 0.2626

```



\*\*Example 2:\*\*

``` text

Text: "ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably wont go back unless someone drags me there"



Results:   

&#x20; "attribution": "likely\_human",

&#x20; "confidence": 0.1646,

&#x20; "content\_id": "63c653b0-e8ac-4bec-a33c-3d4c0ae98850",

&#x20; "creator\_id": "test-user-3",

&#x20; "groq\_score": 0.2,

&#x20; "label": "This content appears to be human-generated. No strong indications of AI use.",

&#x20; "stylometric\_score": 0.1116

```

The AI text scored a 0.585 confidence while the human text scored a 0.165. This demonstrates a signigicant difference between the two and they were labeled into different categories.



\## Transparency Label



\*\*- High-confidence human (score 0.0–0.39):\*\* "This content appears to be human-generated. No strong indications for AI use."



\*\*- Uncertain (score 0.4–0.69):\*\* "The system is not confident about authorship. May be AI-generated, human-generated, or both (could be AI-text slightly altered by a human)."

&#x20;

\*\*- High-confidence AI (score 0.7–1.0):\*\* "This content has been flagged as AI-generated. Strong confidence for AI origins."



\## Limitations

&#x09;Poetry - A poem can cause the system to believe it is AI generated due to the possible repeated word and fixed sentence length that can be found in poetry, triggering the stylometric detection in place.

&#x09;Short Text - Short input text makes it difficult to pick up repeated words or to examine overall sentence length, which is what one of the detection strategies is focused on. This could make the score appear uncertain since it is not confident in either a strictly AI or human author.





\## Spec Reflection



\*\*Spec Helped:\*\* Having set thresholds for the confidence score for the ai/human classification helped to simplify the process. After calculating the score, the confidence score could easily be tied to one of the three classifications with if/else logic.



\*\*Diverged Implementation:\*\* Testing for the score difference in ai/human text led to AI text to be labeled as uncertain when it was expected to be clearly AI. The issue being a fairly low stylometric signal score of 0.26 when the groq score was 0.8 so it fell below the defined threshold of 0.7 when the confidence score was calculated.



\## AI Usage

(at least 2 specific instances describing what you directed the AI to do and what you revised or overrode)



\*\* Instance 1 - M3 (submission endpoint + first signal): \*\* provided claude with the written detection signals and uncertainty representation section of the planning.md. Claude then generated the Flask skeleton with the POST/submit route and the groq signal function. The initial version returned additional text with the score, so revision was needed to explicitly tell the groq prompt to only return a score and nothing else.



\*\* Instance 2- M4 (second signal + confidence scoring): \*\* provided Claude with the written detection signals and uncertainty representation section of the planning.md. Clause then generated the stylometric signal function, scoring logic, and then will combine both of the signals. Ran two examples, one human and one AI, and it returned uncertain on a clear AI sample due to a low stylometric score. Decided to keep the implementation seeing as how this was an expected limitation of the detection signals with short text.



