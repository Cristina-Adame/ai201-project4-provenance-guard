## Architecture Narrative

**Submission Flow**
``` text
+------------------+
| POST /submit     |
| (text,creator\_id)|
+------------------+
        |
        v
+------------------+     +----------------------+
| Signal 1: Groq   |     | Signal 2: Stylometric|
| LLM Score (0-1)  |     | heuristcs (0-1)     |
| semantic/style   |     | variance + TTR       |
+------------------+     +----------------------+
        |                        |
        +----------+-------------+
                   |
                   v
       +-----------------------+
       | Confidence Scoring    |
       | (0.6 \* Groq) +        |
       | (0.4 \* Stylometric)   |
       +-----------------------+
                   |
                   v
       +-----------------------+
       | Transparency Label    |
       | 0.0-0.39 → Human      |
       | 0.4-0.69 → Uncertain  |
       | 0.7-1.0  → AI         |
       +-----------------------+
                   |
                   v
       +-----------------------+
       | JSON Response         |
       | content\_id, scores,   |
       | attribution, label    |
       +-----------------------+
```

## Detection Signals

**Signal 1 — Groq (LLM-based classification)**
- Send the text to Groq with prompt "rate how likely this was written by AI, 0-1" then parse the number back. Selected this because it captures semantic and stylistic coherence holistically.
- Blind spot: possible to be fooled by AI text slightly altered or by human written text with polished grammar/punctuation.

**Signal 2 — Stylometric heuristics**
- Sentence length variance — length of sentence produced by humans will vary more. AI will tend to have a more uniform sentence length.
- Type-token ratio (vocabulary diversity) — the ratio of unique words compared to total words; AI will often reuse the same vocabulary more than human text.
- Blind spot: hard to find variance in text short in length. Structured texts like poetry may be repetitive in words and length, which can be a false positive for an AI flag.

## False Positive Scenario

## API Surface

## Architecture Diagram


## Uncertainty Representation
- 0.0–0.39 → Likely human-written
- 0.4–0.69 → Uncertain
- 0.7–1.0 → Likely AI-generated

Combined score = (0.6 × Groq score) + (0.4 × stylometric score)


## Transparency Label Design

**High-confidence AI (score 0.7–1.0):** "This content has been flagged as AI-generated. Strong confidence for AI origins."
**Uncertain (score 0.4–0.69):** "The system is not confident about authorship. May be AI-generated, human-generated, or both (could be AI-text slightly altered by a human)."
**High-confidence human (score 0.0–0.39):** "This content appears to be human-generated. No strong indications for AI use."


## Appeals Workflow

User may submit an appeal if they believe their AI flagged material was mislabeled. Appeal request will need to include the id of the submission and their written reasoning. When received, the status will be changed to 'under review' and it will be logged alongside the original system classification. Must be reviewed by a person and not another AI system.


## Anticipated Edge Cases
1. Poetry - A poem can cause the system to believe it is AI generated due to the possible repeated word and fixed sentence length that can be found in poetry, triggering the stylometric detection in place.
2. Short Text - Short input text makes it difficult to pick up repeated words or to examine overall sentence length, which is what one of the detection strategies is focused on. This could make the score appear uncertain since it is not confident in either a strictly AI or human author.


## AI Tool Plan

**M3 (submission endpoint + first signal):** will provide claude with the the written detection signals and uncertainty representation section of the planning.md. Claude will then generated the Flask skeleton with the POST/submit route and the groq signal function. Will verify it works by ensuring Groq returns a score between 0 and 1.

**M4 (second signal + confidence scoring):** will provide claude with the the written detection signals and uncertainty representation section of the planning.md. Clause will then generate the stylometric signal function, scoring logic, and then will combine both of the signals. Will verify by running with AI text and human text and checking to see both received different enough scores.

** M5 (production layer): **
