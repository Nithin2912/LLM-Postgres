# Brand/Manufacturer Autofill (PostgreSQL + OpenAI)

A clean, **structured** Python project that fills missing `brand` and `manufacture` fields in your Postgres table by using:
1) fast **heuristics** from `product_name`
2) **LLM** fallback (OpenAI) when heuristics aren't confident

Updates are applied **in-place** to your table, and an **audit** table logs changes.

## Requirements
- Python 3.11+ (Windows: install from https://www.python.org/downloads/windows/ and check “Add Python to PATH”)
- PostgreSQL reachable from your machine
- OpenAI API key

## Project Structure
(see tree above)

## Environment Variables
Copy `.env.example` to `.env` and fill in your values:
