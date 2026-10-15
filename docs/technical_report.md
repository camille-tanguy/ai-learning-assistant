# AI Learning Assistant

## Technical Project Report

**Project:** Automated AI Research Curation & Learning Assistant  
**Platform:** n8n Cloud  
**Technologies:** JavaScript, Telegram Bot API, Google Sheets, OpenRouter, arXiv RSS, Hugging Face API  
**Project Level:** Level 3 — Advanced

---

# 1. Introduction

## 1.1 Background and Motivation

The rapid development of artificial intelligence has resulted in a growing volume of research publications. Platforms such as arXiv and Hugging Face provide access to recent research, but identifying relevant and educational contributions across multiple sources requires considerable time.

For students, developers, and AI practitioners, manually reviewing publications can be inefficient, particularly when the same papers appear across different platforms.

The AI Learning Assistant addresses this challenge through an automated research curation and learning system built using n8n.

Rather than simply aggregating publications, the application combines deterministic data processing with selective large language model (LLM) analysis to identify and explain relevant research developments.

## 1.2 Project Objectives

The primary objective is to develop a modular automation system capable of collecting, processing, evaluating, and organizing recent AI research publications.

The application is designed to:

1. Retrieve research papers from reliable external sources.
2. Normalize heterogeneous data into a consistent structure.
3. Identify duplicate publications before AI processing.
4. Filter and rank articles using deterministic algorithms.
5. Apply LLM-based semantic evaluation to selected candidates.
6. Generate a curated daily digest of up to five publications.
7. Store research metadata and generated digests persistently.
8. Provide interactive access through a Telegram bot.
9. Minimize operating costs by limiting unnecessary LLM inference.

The project targets Level 3 of the course's workflow automation framework through its integration of external APIs, branching logic, persistent storage, reusable sub-workflows, and AI processing.

## 1.3 Design Philosophy

The central design principle is:

**AI-powered, not AI-dependent.**

Traditional programming techniques are preferred for operations that do not require semantic understanding, including normalization, deduplication, keyword filtering, numerical ranking, and command routing.

LLMs are reserved for tasks where they provide additional value, particularly evaluating research contributions and generating educational explanations.

This separation aims to improve cost efficiency, transparency, and maintainability.

---

# 2. System Architecture

## 2.1 Architectural Overview

The AI Learning Assistant is implemented using n8n Cloud and organized into four workflows.

The architecture separates research ingestion, semantic analysis, persistent storage, and user interaction.

This modular design allows individual components to be tested and modified independently while maintaining a clear separation of responsibilities.

The system supports three execution mechanisms:

- **Scheduled execution:** Automatically initiates the research processing pipeline.
- **Manual execution:** Allows the pipeline to be tested and executed on demand.
- **Telegram interaction:** Processes user commands and retrieves or generates information.

Google Sheets acts as the persistent data layer, while OpenRouter provides access to language models.

## 2.2 Workflow Organization

### 01 — Telegram Connection

The Telegram Connection workflow is a dedicated integration test.

It consists of three nodes:

```text
Telegram Trigger
       |
       v
      IF
       |
       v
Telegram Response
```

Its purpose is to verify that n8n can receive Telegram messages and send responses.

The workflow is maintained separately from the main user interaction workflow.

### 02 — AI Daily Pipeline

The AI Daily Pipeline is the central data-processing component.

It retrieves recent research publications, standardizes their structure, removes duplicates, filters candidates, performs AI-assisted evaluation, and stores the highest-ranked publications.

Its execution follows this sequence:

```text
Manual / Schedule / Sub-workflow Trigger
                   |
          +--------+--------+
          |                 |
          v                 v
   Hugging Face API      arXiv RSS
          |                 |
          v                 v
      Normalize         Normalize
          |                 |
          +--------+--------+
                   |
                   v
              Merge Data
                   |
                   v
        Load Existing Articles
                   |
                   v
            Deduplication
                   |
                   v
          Keyword Filtering
                   |
                   v
        Deterministic Ranking
                   |
                   v
          Top 30 Candidates
                   |
                   v
        03 - Article Analysis
                   |
                   v
             Final Ranking
                   |
                   v
                 Top 5
                   |
                   v
              Google Sheets
                   |
                   v
           Store Daily Digest
```

The pipeline generates and stores the daily digest in Google Sheets.

In the current implementation, scheduled execution does not automatically deliver the digest through Telegram. Users retrieve it through the interaction workflow.

### 03 — Article Analysis

Article Analysis is implemented as a reusable n8n sub-workflow.

It receives normalized article information and evaluates the publication using an LLM accessed through OpenRouter.

The model generates:

- A concise technical explanation.
- An explanation of the publication's significance.
- A research category.
- Relevance, learning, and novelty scores.
- Key takeaways.

The generated output is parsed and validated using JavaScript before being returned to the main pipeline.

Separating this functionality into a sub-workflow avoids duplicating LLM-processing logic.

### 04 — Telegram Interaction

The Telegram Interaction workflow provides the user-facing interface.

A Telegram Trigger receives messages, while a Switch node routes commands to dedicated processing branches.

| Command | Function | LLM Required |
| --------- | ---------- | -------------- |
| `/start` | Welcome message and digest availability check | No |
| `/help` | Display available commands | No |
| `/daily` | Retrieve the latest stored digest | No |
| `/learn [article_id]` | Generate a deeper explanation | Yes |

The `/start` workflow can also initiate digest generation when no digest is available for the current day.

The `/learn` command retrieves stored article information before invoking an LLM to produce an educational explanation.

The `/like` command is not implemented in the exported version and remains a potential future improvement.

## 2.3 Technology Stack

| Technology | Purpose |
| ------------ | --------- |
| n8n Cloud | Workflow orchestration |
| JavaScript | Data transformation, filtering, and ranking |
| Hugging Face API | Research paper discovery |
| arXiv RSS | Research paper discovery |
| OpenRouter | LLM inference |
| Google Sheets | Persistent storage |
| Telegram Bot API | User interaction |
| Python | Sanitization of workflow exports |
| Git and GitHub | Version control and documentation |

## 2.4 Data Persistence

Google Sheets provides persistent storage through two worksheets.

**ARTICLES** stores publication identifiers, metadata, AI-generated explanations, evaluation scores, and processing timestamps.

**DAILY_DIGEST** stores digest dates, selected article identifiers, formatted digest text, and timestamps.

The implementation uses dedicated fields such as `what_it_does` and `why_it_matters` for generated explanations.

Although the ARTICLES schema also includes a `summary` column, the current Article Analysis workflow does not explicitly populate that field.

Google Sheets was selected because of its simplicity, accessibility, and native integration with n8n.

This approach avoids the infrastructure overhead of maintaining a dedicated database server for a small-scale academic application.

---

# 3. Data Collection and Processing

## 3.1 Research Data Collection

The system retrieves publications from two external sources:

- Hugging Face Daily Papers API.
- arXiv Computer Science — Artificial Intelligence (cs.AI) RSS feed.

Both sources are accessed through n8n HTTP Request nodes.

Retrieved information includes publication titles, URLs, dates, descriptions, and paper identifiers.

Using multiple sources increases research coverage but introduces duplicate records, since Hugging Face frequently features papers originally published on arXiv.

Consequently, normalization and deduplication are performed before semantic analysis.

## 3.2 Data Normalization

The two sources provide data in different formats.

Dedicated JavaScript Code nodes transform incoming records into a common representation.

The normalized article structure includes:

| Field | Description |
| ------- | ------------- |
| `article_id` | Internal article identifier |
| `arxiv_id` | arXiv paper identifier |
| `title` | Publication title |
| `url` | Article URL |
| `original_url` | Original publication URL |
| `quick_read_url` | Alternative reading link |
| `source` | Publication source |
| `published_at` | Publication date |
| `description` | Abstract or description |
| `content` | Text available for analysis |
| `featured_on_huggingface` | Hugging Face inclusion indicator |
| `processed` | Processing status |

Additional fields are initialized for subsequent AI evaluation.

The Hugging Face normalization node also excludes records without a valid paper identifier or title.

Normalizing data early simplifies downstream processing by allowing different research sources to share the same workflow logic.

## 3.3 Deduplication

The pipeline implements deterministic deduplication using JavaScript.

Its primary identifier is the arXiv paper ID.

The process consists of three stages:

1. Retrieve previously stored articles from Google Sheets.
2. Merge incoming records referring to the same arXiv publication.
3. Exclude articles whose identifiers are already present in persistent storage.

JavaScript `Set` and `Map` objects support efficient identifier lookup and record merging.

When the same paper appears in both arXiv and Hugging Face, the algorithm attempts to preserve useful information from both sources.

For example, a combined record may retain the original arXiv URL while preserving a Hugging Face quick-reading link.

This mechanism reduces redundant processing and repeated LLM analysis.

However, its reliability depends on consistent article identifiers. Publications without compatible arXiv identifiers may require additional URL-based deduplication.

## 3.4 Deterministic Relevance Filtering

After deduplication, the application evaluates article relevance through predefined keywords.

The keyword list includes concepts such as:

- Artificial intelligence
- Machine learning
- Deep learning
- Large language models
- Computer vision
- Neural networks
- Transformers
- Reinforcement learning
- Multimodal AI
- Robotics

The filtering algorithm combines each article's title and description, converts the text to lowercase, and checks whether the predefined expressions are present.

An article passes the filter when at least one keyword matches.

The algorithm records the number of distinct keyword expressions matched.

This operation requires no LLM inference and provides an inexpensive first-stage relevance filter.

However, keyword matching is not equivalent to semantic understanding. Relevant publications may be excluded if they use unfamiliar terminology.

## 3.5 Preliminary Ranking

Articles passing the relevance filter receive a deterministic score.

The implemented formula is:

```text
Deterministic Score =
    2 × Keyword Match Count
  + Content Length Bonus
```

The content-length bonus is defined as:

```text
Content Length Bonus =
    1 if title + description exceeds 800 characters
    0 otherwise
```

Articles are sorted by their deterministic scores in descending order.

Only the 30 highest-ranked candidates are retained for AI analysis.

This limit controls the maximum number of article-analysis requests during a normal pipeline execution.

The preliminary ranking is intentionally simple and transparent.

Its purpose is not to identify the scientifically strongest publications, but to reduce the candidate set before more expensive semantic evaluation.

---

# 4. AI Integration and Ranking Methodology

## 4.1 LLM Integration

The application integrates language models through OpenRouter using the native n8n OpenRouter Chat Model node.

The configured model identifier is:

```text
openrouter/free
```

This configuration accesses OpenRouter's free-model routing, subject to provider availability and usage limitations.

LLM inference is used for two operations:

1. Structured evaluation of selected research papers.
2. On-demand educational explanations through Telegram.

All other major data-processing and routing operations rely on deterministic logic.

## 4.2 Article Analysis

The Article Analysis sub-workflow receives publication metadata, including the title and description.

The LLM prompt requests structured output containing seven fields.

| Field | Purpose |
| ------- | --------- |
| `what_it_does` | Explain the technical contribution |
| `why_it_matters` | Explain its practical or educational significance |
| `category` | Assign a research category |
| `relevance_score` | Evaluate relevance to AI/ML/software engineering |
| `learning_score` | Evaluate educational value |
| `novelty_score` | Evaluate perceived novelty |
| `key_takeaways` | Identify important learning points |

The numerical scores range from 0 to 10.

The prompt requests valid JSON without Markdown formatting or additional text.

An illustrative response is:

```json
{
  "what_it_does": "The paper introduces a method for improving model efficiency.",
  "why_it_matters": "The approach may reduce computational requirements.",
  "category": "Model Optimization",
  "relevance_score": 8,
  "learning_score": 9,
  "novelty_score": 7,
  "key_takeaways": [
    "Understanding computational efficiency",
    "Exploring model optimization techniques"
  ]
}
```

This example illustrates the expected format rather than representing a measured model output.

## 4.3 Output Validation

LLM responses may contain formatting errors, missing fields, or invalid numerical values.

The Article Analysis workflow therefore includes a JavaScript validation node named `Parse & Validate Analysis`.

The node:

1. Removes possible Markdown code fences.
2. Parses the response using `JSON.parse()`.
3. Verifies the presence of required fields.
4. Checks that numerical scores are between 0 and 10.
5. Confirms that explanation fields contain non-empty strings.
6. Verifies that key takeaways form a non-empty array.

The result is stored in a Boolean field named `valid_json`.

Invalid analyses are excluded from the final ranking.

This validation improves structural reliability but does not guarantee the factual correctness of generated explanations.

## 4.4 Final Ranking

Each valid publication receives three model-generated scores:

- Relevance.
- Learning value.
- Novelty.

The final score is calculated deterministically:

```text
Final Score =
    0.40 × Relevance Score
  + 0.35 × Learning Score
  + 0.25 × Novelty Score
```

Relevance receives the highest weight because the system prioritizes research directly connected to AI, machine learning, and software engineering.

Learning value receives the second-highest weight, reflecting the application's educational purpose.

Novelty receives a smaller weight to prevent unfamiliar or unusual research from dominating the ranking solely because of its perceived originality.

The five highest-scoring valid publications are selected.

These weights are design choices rather than empirically optimized parameters.

## 4.5 On-Demand Learning

The `/learn [article_id]` command provides deeper explanations of selected publications.

The Telegram workflow retrieves the requested article from Google Sheets and supplies its stored information to an LLM.

The generated response follows four educational sections:

1. Big idea.
2. How it works.
3. Why it matters.
4. What you can learn from it.

Unlike the structured article-analysis workflow, this component produces human-readable text for direct delivery through Telegram.

The model is instructed to avoid introducing information unsupported by the available article data.

Nevertheless, the explanation is generated from stored summaries and metadata rather than a complete independent analysis of the research paper.

---

# 5. Cost Optimization

## 5.1 Cost-Aware Design

Minimizing operating costs is a central objective of the application.

LLM inference may introduce API charges, latency, and external service dependencies.

The system therefore performs normalization, deduplication, filtering, and preliminary ranking before invoking a language model.

This design reduces unnecessary inference while maintaining semantic analysis for high-value candidates.

## 5.2 Deterministic Versus AI Processing

The application separates conventional data-processing operations from tasks requiring semantic reasoning.

| Operation | Processing Method |
| ----------- | ------------------- |
| Research retrieval | HTTP Request |
| Normalization | JavaScript |
| Deduplication | JavaScript and Google Sheets |
| Keyword filtering | JavaScript |
| Preliminary ranking | JavaScript |
| Article analysis | LLM |
| Final score calculation | JavaScript |
| Digest formatting | JavaScript |
| `/help` | Deterministic |
| `/daily` | Google Sheets retrieval |
| `/learn` | LLM |

This separation avoids using an LLM for operations that can be performed reliably through conventional programming.

## 5.3 Candidate Reduction

The pipeline applies successive filtering operations before semantic analysis.

Let:

- N = total number of retrieved records.
- D = number of distinct new articles.
- R = number of articles passing relevance filtering.
- A = number of articles selected for LLM analysis.

The pipeline satisfies:

```text
A = min(R, 30)

A <= R <= D <= N
```

For illustration, consider a hypothetical execution retrieving 100 article records.

After deduplication, 70 distinct new publications remain.

Keyword filtering reduces this number to 45 relevant candidates.

The deterministic ranking stage then selects 30 articles for LLM analysis.

The corresponding reduction in article-analysis requests is:

```text
Without preprocessing: 100 requests

With preprocessing:     30 requests

Reduction:              70%
```

This example is hypothetical and does not represent a measured result from the application.

Actual inference savings depend on source overlap, previously processed publications, and keyword-filtering outcomes.

## 5.4 Operating Costs and Limitations

The system relies on publicly accessible research sources and OpenRouter's free-model routing to minimize external service costs.

However, free-model availability, request limits, and provider conditions may change.

Furthermore, n8n Cloud hosting may involve subscription costs independently of LLM inference.

The current implementation does not include dedicated monitoring of token consumption or API expenses.

Consequently, the architecture demonstrates cost-aware design, but its financial efficiency has not yet been quantified through systematic measurements.

---

# 6. Testing, Validation and Results

## 6.1 Testing Strategy

The application integrates several external systems, making both component-level and end-to-end validation necessary.

Testing is organized around three levels:

**Component testing:** Verification of individual nodes and JavaScript transformations.

**Integration testing:** Verification of communication between n8n workflows and external services.

**End-to-end testing:** Verification that the complete application retrieves, processes, stores, and displays research information.

The workflows have been exercised during development, but the exported configuration alone does not provide complete execution logs or quantitative reliability measurements.

The following tests define the expected behavior and the evidence required for reproducible validation.

## 6.2 Functional Testing

| Component | Expected Behavior | Evidence |
| ----------- | ------------------- | ---------- |
| Telegram connection | Receive and respond to messages | Telegram execution screenshot |
| Research ingestion | Retrieve publications from both sources | n8n execution output |
| Normalization | Produce a consistent article structure | Code node output |
| Deduplication | Exclude previously processed publications | Before/after article records |
| Article analysis | Return structured evaluation data | Sub-workflow output |
| JSON validation | Reject malformed model responses | Validation output |
| Final ranking | Select up to five valid articles | Ranking node output |
| Data persistence | Store selected articles and digests | Google Sheets records |
| `/daily` | Retrieve the latest digest | Telegram screenshot |
| `/learn` | Generate an educational explanation | Telegram screenshot |

These entries describe test scenarios and expected outcomes.

They should be accompanied by execution evidence before being presented as systematically verified results.

## 6.3 Reliability Mechanisms

Several reliability mechanisms are implemented.

### External API Retries

The Hugging Face and arXiv HTTP Request nodes include retry configurations.

They also use continue-on-error behavior, allowing failures to be passed downstream.

However, this does not guarantee successful recovery from every external service failure.

Downstream normalization may still fail when required response fields are unavailable.

### LLM Output Validation

The Article Analysis workflow parses model responses and verifies the expected JSON structure.

Invalid analyses are excluded from the final ranking stage.

This reduces the risk of malformed outputs reaching persistent storage.

### Telegram Input Validation

The Telegram workflow validates article identifiers before executing the `/learn` functionality.

Missing or unknown identifiers are handled through dedicated response branches.

### Telegram Message Length

The workflow includes JavaScript logic for splitting long digest messages into smaller sections.

This reduces the risk of exceeding Telegram's message length limit, although unusually long individual sections may still require additional handling.

## 6.4 Execution Results

A successful execution of the AI Daily Pipeline was examined
to evaluate the behavior of the data-processing stages.

The execution retrieved 1,403 research article records from
Hugging Face Daily Papers and arXiv.

After deduplication, 1,388 records remained, indicating that
15 records were excluded because they duplicated incoming
publications or matched previously stored articles.

The deterministic relevance filter retained 1,035 articles
and rejected 353 articles that did not match the predefined
AI-related keywords.

The preliminary ranking stage then selected the 30
highest-scoring candidates for LLM-based analysis.

Following AI evaluation and final ranking, five research
papers were selected for the daily digest.

### Observed Processing Results

| Processing Stage | Articles |
| ------------------ | ---------: |
| Retrieved article records | 1,403 |
| Records excluded by deduplication | 15 |
| Articles after deduplication | 1,388 |
| Articles rejected by keyword filtering | 353 |
| Articles passing keyword filtering | 1,035 |
| Candidates selected for AI analysis | 30 |
| Articles selected for daily digest | 5 |
| Daily digest records generated | 1 |

### Execution Performance

Execution records from October 15, 2026 provide
evidence of successful workflow operation.

| Workflow | Execution Status | Duration |
| ---------- | ------------------ | ---------- |
| AI Daily Pipeline | Succeeded | 12 min 55.148 s |
| Article Analysis (single article) | Succeeded | 19.146 s |
| Telegram Interaction | Succeeded | 2.292 s |

The complete AI Daily Pipeline required approximately
12 minutes and 55 seconds to finish processing.

The duration includes research retrieval, data
transformations, Google Sheets operations, sequential
article analysis, and digest generation.

The Article Analysis sub-workflow completed one
observed execution in approximately 19 seconds.

The Telegram Interaction workflow completed one
observed execution in approximately 2.3 seconds.

These measurements describe individual executions
rather than average system performance.

Additional observations would be required to
evaluate execution-time variability or establish
reliable performance benchmarks.

### Reduction in LLM Analysis Volume

The pipeline limits the number of articles submitted to
LLM analysis through deterministic preprocessing.

For this execution:

- Initial retrieved records: 1,403
- Candidates selected for AI analysis: 30

The reduction in article-analysis volume is calculated as:

Reduction = (1,403 - 30) / 1,403 × 100

Reduction = 97.9%

Therefore, the deterministic preprocessing and candidate
selection stages reduced the number of articles selected
for LLM analysis by approximately 97.9% relative to
analyzing every retrieved record.

This result demonstrates the effectiveness of the
architecture in controlling inference volume.

However, the figure does not represent measured API
cost savings or token consumption.

Furthermore, the reduction is partly attributable to
the fixed Top 30 candidate limit rather than relevance
filtering alone.

### Digest Generation

The final ranking stage selected five publications.

The Format Daily Digest node successfully generated one
structured digest containing the selected articles.

The resulting digest was prepared for persistent storage
in Google Sheets.

## 6.5 Reliability Limitations

The implementation currently lacks automated regression tests and comprehensive execution monitoring.

External API failures, changes in response structures, free-model unavailability, and Google Sheets connection errors may still interrupt processing.

Additionally, structural validation cannot detect scientifically inaccurate model-generated explanations.

The existing safeguards therefore improve reliability but do not establish production-grade fault tolerance.

---

# 7. Limitations and Future Improvements

## 7.1 Current Limitations

The application demonstrates a functional approach to automated research curation, but its capabilities remain limited in several areas.

**Research coverage:** The system uses only two research sources. Relevant developments published through technical blogs, software engineering repositories, or other research categories may be excluded.

**Relevance filtering:** Keyword-based filtering is inexpensive and interpretable but may exclude relevant publications that use unfamiliar terminology.

**LLM evaluation:** Article analysis relies primarily on titles and descriptions rather than complete research papers. Generated scores are subjective and are not independently validated against expert assessments.

**Data storage:** Google Sheets provides convenient persistence but is less suitable for high-volume applications requiring advanced querying or concurrent updates.

**Operational reliability:** Retry and validation mechanisms exist, but comprehensive monitoring, automated tests, and recovery procedures have not been implemented.

**Personalization:** The current exported Telegram workflow does not include user-feedback-based recommendations.

## 7.2 Future Improvements

Future development should prioritize improvements that provide measurable benefits without significantly increasing operating costs.

| Improvement | Expected Benefit | Priority |
| ------------- | ------------------ | ---------- |
| Automated tests | Improved reliability | High |
| Execution monitoring | Better observability | High |
| Automatic Telegram delivery | More proactive user experience | High |
| Additional research sources | Broader coverage | Medium |
| `/like` feedback command | User preference tracking | Medium |
| LLM evaluation benchmark | Better analysis quality | Medium |
| Database migration | Improved scalability | Low |

### Automated Testing and Monitoring

A future version could introduce systematic tests for normalization, deduplication, ranking, and JSON validation.

Execution metrics could also be stored to track article counts, failures, processing duration, and token consumption.

This would enable objective evaluation of the application's efficiency and reliability.

### User Feedback and Personalization

A `/like [article_id]` command could allow users to express interest in specific publications.

Feedback could be stored in a dedicated Google Sheets worksheet.

A simple personalization mechanism could then adjust ranking weights according to preferred categories without requiring additional LLM inference.

### Improved Research Coverage

Additional reliable RSS feeds and public APIs could broaden the system's coverage.

However, new sources should only be introduced when they provide meaningful information not already represented in existing feeds.

### Automated Telegram Delivery

The scheduled pipeline currently generates and stores digests without automatically sending them to Telegram.

A future extension could deliver newly generated digests directly to subscribed users.

This would improve the user experience without requiring additional LLM processing.

## 7.3 Development Priorities

The recommended development strategy is incremental.

Reliability, observability, and user experience should be improved before introducing more complex AI capabilities.

This approach is consistent with the project's original objective of maintaining a low-cost, understandable, and maintainable architecture.

---

# 8. Conclusion

The AI Learning Assistant demonstrates the development of a modular automation system combining external research sources, deterministic data processing, LLM-based evaluation, persistent storage, and conversational interaction.

Built using n8n Cloud, the application retrieves recent AI research papers from arXiv and Hugging Face, normalizes and deduplicates publications, filters relevant candidates, and generates a curated Top 5 daily digest.

Users can retrieve stored digests and request deeper explanations through Telegram.

The project's central technical contribution is its cost-aware architecture.

By performing normalization, deduplication, relevance filtering, numerical ranking, and command routing without an LLM, the system limits inference to tasks requiring semantic understanding.

The implementation also demonstrates important software engineering practices, including modular workflow design, structured data transformations, reusable sub-workflows, API integration, and validation of model-generated outputs.

Several limitations remain, particularly regarding semantic evaluation quality, external service reliability, and the absence of systematic performance measurements.

Future development should prioritize automated testing, execution monitoring, and user feedback before introducing additional complexity.

Overall, the project illustrates how conventional software engineering techniques and targeted AI integration can be combined to create a practical, maintainable, and cost-conscious research learning assistant.
