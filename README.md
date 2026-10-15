# AI Learning Assistant

An automated AI research and learning assistant built with
n8n, Telegram, OpenRouter, and Google Sheets.

## Overview

AI Learning Assistant automatically collects recent AI research
papers, filters and ranks relevant content, and generates a
curated daily digest.

Users can interact with the assistant through Telegram to
retrieve research updates and explore individual papers.

## Tech Stack

- n8n — Workflow automation
- Telegram Bot API — User interface
- Hugging Face & arXiv — Research sources
- OpenRouter — LLM integration
- Google Sheets — Data persistence

## Features

- Automated daily research collection
- Duplicate detection
- Deterministic relevance filtering
- AI-powered article analysis
- Top 5 research ranking
- Google Sheets storage
- Telegram commands: /start, /help, /daily, /learn

## Architecture

The project is organized into four n8n workflows:

1. Telegram Connection
2. AI Daily Pipeline
3. Article Analysis
4. Telegram Interaction

## Project Status

Core workflows implemented and tested.
Documentation and deployment instructions are being prepared.
