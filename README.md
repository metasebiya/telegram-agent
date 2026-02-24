# 🤖 LangGraph Telegram Agent 

A state-of-the-art Telegram bot built with **LangGraph**, featuring
durable execution, asynchronous persistence, and **"Time Travel" state
recovery**.

This agent doesn't just chat --- it remembers every version of its
thoughts and can resume from a crash without losing a single token.

------------------------------------------------------------------------

## ✨ Key Features

-   **Durable Execution:** If the bot server crashes mid-task, it
    resumes exactly where it left off upon restart.
-   **Time Travel (State History):** View every draft iteration using
    `/history` and instantly revert to any past version with `/rewind`.
-   **Human-in-the-Loop:** A built-in **Approval gate** ensures no
    content is posted to your channel without your explicit `/approve`
    command.
-   **Asynchronous Persistence:** Powered by `AsyncSqliteSaver` and
    `aiosqlite` for non-blocking database I/O.
-   **Flexible Model Support:** Compatible with OpenAI, Google Gemini,
    and Groq.

------------------------------------------------------------------------

## 🚀 Quick Start

### 1️⃣ Prerequisites

Ensure you have the **uv** package manager installed (the 2026 standard
for Python).

``` bash
# Install dependencies
uv sync
uv add aiosqlite langgraph-checkpoint-sqlite
```

------------------------------------------------------------------------

### 2️⃣ Environment Setup

Create a `.env` file in the root directory:

``` plaintext
TELEGRAM_TOKEN=your_bot_token
CHANNEL_ID=@your_channel_handle
OPENAI_API_KEY=your_key_or_gemini_key
```

------------------------------------------------------------------------

### 3️⃣ Run the Agent

``` bash
uv run main.py
```

------------------------------------------------------------------------

## 🛠 Usage Commands

  -----------------------------------------------------------------------
  Command                                 Action
  --------------------------------------- -------------------------------
  `Topic text...`                         Send any text to have the AI
                                          generate a draft post

  `/approve`                              Moves the graph past the
                                          approval node and posts to the
                                          channel

  `/history`                              Displays recent
                                          `checkpoint_ids` and draft
                                          snippets

  `/rewind <id>`                          Reverts the agent's memory to
                                          that specific checkpoint
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 🏗 Architecture

The agent is built using a **directed cyclic graph**:

-   **Creator Node:** Generates the content using the LLM\
-   **Approval Node:** An interrupt point that pauses execution\
-   **Persistence Layer:** Every state change is hashed and saved to
    `checkpoints.db`

------------------------------------------------------------------------

## 📝 License

**MIT License**\
© 2026 Tenacious Training TRP Tutorials
