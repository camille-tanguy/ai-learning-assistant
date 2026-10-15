# Installation and Setup Guide

## 1. Prerequisites

To reproduce the AI Learning Assistant, you will need:

- An n8n instance (Cloud or self-hosted)
- A Telegram account
- A Telegram bot created using BotFather
- A Google account with access to Google Sheets
- An OpenRouter account and API key
- Internet access to retrieve research papers

The project uses public research sources and OpenRouter's
free model routing to minimize operating costs.

## 2. Import the n8n Workflows

The repository contains four workflow exports in `workflows/`:

1. `01- Telegram Connection Test.json`
2. `02 - AI Daily Pipeline.json`
3. `03 - Article Analysis.json`
4. `04 - Telegram Interaction.json`

For each workflow:

1. Open your n8n instance.
2. Create a new workflow.
3. Open the workflow menu (three dots).
4. Select **Import from File**.
5. Choose the corresponding JSON file.
6. Save the imported workflow.

Import all four workflows before configuring their connections.

The JSON files have been sanitized for public distribution.
Credentials and instance-specific identifiers must be configured
after importing.

## 3. Configure Telegram

### Create a Telegram Bot

1. Open Telegram.
2. Search for `@BotFather`.
3. Send `/newbot`.
4. Follow the instructions to create your bot.
5. Copy the bot token.

### Connect Telegram to n8n

1. Open `04 - Telegram Interaction`.
2. Select the `Receive Telegram Command` node.
3. Create a new Telegram credential.
4. Enter the token provided by BotFather.
5. Save the credential.

Select the same credential for the Telegram message nodes.

Use `01 - Telegram Connection Test` to verify communication
between your Telegram bot and n8n.

**Important:** Only activate one Telegram Trigger workflow
for the same bot at a time to avoid webhook conflicts.

Do not commit your Telegram bot token to GitHub.

## 4. Configure Google Sheets

Create a Google Sheets spreadsheet named:

`AI Learning Assistant Database`

Create two worksheets:

### ARTICLES

Add these columns in the first row:

```text
article_id
title
url
source
published_at
category
summary
relevance_score
learning_score
novelty_score
processed_at
arxiv_id
original_url
quick_read_url
featured_on_huggingface
final_score
what_it_does
why_it_matters
```

### DAILY_DIGEST

Add these columns:

```text
date
article_ids
digest_text
sent_at
```

### Connect Google Sheets to n8n

1. Create Google Sheets credentials in n8n.
2. Open each Google Sheets node.
3. Select your Google Sheets credentials.
4. Select your spreadsheet.
5. Select the appropriate worksheet.
6. Verify the column mappings.

The public workflow exports contain a placeholder for the
Google Sheets document ID, so you must select your own spreadsheet.

## 5. Configure OpenRouter

1. Create an account at <https://openrouter.ai>.
2. Generate an API key.
3. Open `03 - Article Analysis`.
4. Select the `OpenRouter Chat Model` node.
5. Create an OpenRouter credential using your API key.
6. Configure the model.

The project uses:

```text
openrouter/free
```

Repeat the credential configuration for the
`Free OpenRouter Model` node in `04 - Telegram Interaction`.

Free-model availability, limits, and routing may change.
Check OpenRouter's current conditions before running the workflows.

## 6. Reconnect Sub-workflows

The exported JSON files contain placeholder workflow references.

These must be reconfigured after importing.

### AI Daily Pipeline

Open:

`02 - AI Daily Pipeline`

Find:

`Call '03 - Article Analysis'`

Select the imported:

`03 - Article Analysis`

### Telegram Interaction

Open:

`04 - Telegram Interaction`

Find:

`02 - AI Daily Pipeline`

Select the imported:

`02 - AI Daily Pipeline`

Save both workflows.

## 7. Test the Application

### Test Article Analysis

1. Open `03 - Article Analysis`.
2. Execute it with sample article data.
3. Verify that the output contains the expected analysis fields.
4. Confirm that `valid_json` is `true`.

### Test the Daily Pipeline

1. Open `02 - AI Daily Pipeline`.
2. Execute it manually.
3. Verify that articles are retrieved from Hugging Face and arXiv.
4. Check that duplicate articles are filtered.
5. Verify that relevant articles are analyzed.
6. Confirm that the Top 5 articles are stored in Google Sheets.
7. Check that a new row appears in `DAILY_DIGEST`.

### Test Telegram Interaction

Activate `04 - Telegram Interaction`.

Open your Telegram bot and test:

```text
/start
/help
/daily
/learn A-[arxiv_id]
```

Replace `[arxiv_id]` with an identifier stored in your
ARTICLES worksheet.

Verify that each command returns the expected response.

## 8. Scheduling

The Daily Pipeline includes a Schedule Trigger
configured to run daily at 09:00 in the workflow's timezone.

Verify the timezone in your n8n configuration.

Activate the workflow only after testing the complete pipeline.

## 9. Security

Never commit:

- Telegram bot tokens
- OpenRouter API keys
- Google OAuth credentials
- `.env` files containing secrets
- Original n8n exports containing private identifiers

The repository includes a Python sanitization script:

```bash
python3 sanitize_workflows.py
```

Original workflow exports should be placed in
`private_exports/`, which is excluded through `.gitignore`.

The sanitized JSON files are generated in `workflows/`.

Review the generated files before committing them.

## 10. Known Limitations

- LLM-generated analysis can occasionally be inaccurate.
- Free LLM endpoints may be rate-limited or unavailable.
- Workflow references must be reconfigured after import.
- Google Sheets is suitable for a small project but is not
  intended as a high-throughput production database.
- The public exports do not include API credentials.
- Importing the workflows does not automatically recreate
  the Google Sheets database.
