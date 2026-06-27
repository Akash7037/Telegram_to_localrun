# Energy-Efficient Telegram AI Laptop Assistant

This project implements an energy-efficient Python application that runs in the background on Windows laptops. It acts as an AI-powered assistant, listening for commands from a specific Telegram chat and executing corresponding system tasks. The core design prioritizes minimal resource consumption and robust error handling.

## Features

*   **Energy-Efficient Operation:** Only active when the laptop is plugged in and charging, pausing automatically when on battery power.
*   **Telegram Integration:** Securely listens for messages from a whitelisted Telegram chat using long-polling.
*   **Intelligent Classification:** Uses a two-stage classification system:
    *   **Local Heuristic:** Quickly identifies casual messages using keyword matching to reduce LLM calls.
    *   **LLM Fallback:** Leverages small, remote LLMs (e.g., GPT-4o-mini, Claude Haiku) for complex command intent classification.
*   **Extensible Command Execution:** A modular system for executing various laptop tasks, including:
    *   Opening browser searches (e.g., YouTube, Google)
    *   Putting the laptop to sleep
    *   Shutting down the laptop
    *   Locking the screen
    *   Opening and closing applications
*   **Robust Error Handling:** Implements `try/except` blocks, exponential backoff for network retries, and graceful degradation to prevent crashes.
*   **Secure Configuration:** Uses `.env` files for sensitive API keys and whitelisted chat IDs, never hardcoding credentials.
*   **Comprehensive Logging:** Rotates log files to prevent excessive growth, capturing timestamps, messages, classifications, actions, and errors.

## Architecture Overview

The assistant is composed of several key modules:

*   **Main Application Orchestrator (`main.py`):** Manages the overall application lifecycle, coordinating the Power Watcher and Telegram Listener.
*   **Power Watcher:** Monitors the laptop's charging status (`psutil`) and activates/deactivates the Telegram Listener accordingly.
*   **Telegram Listener (`listener.py`):** Handles incoming messages from Telegram, ensuring only whitelisted users can send commands.
*   **Classifier (`classifier.py`):** Determines the intent of messages using a local heuristic and an LLM fallback.
*   **Command Executor (`executor.py`):** Maps classified commands to specific system actions and executes them.
*   **Logging (`logger.py`):** Manages application logs, writing to a rotating file.
*   **Configuration (`config.py`):** Loads and validates settings from the `.env` file.

## Setup Instructions

Follow these steps to get your Energy-Efficient Telegram AI Laptop Assistant up and running on Windows.

### 1. Prerequisites

*   **Python 3.10+:** Download and install from [python.org](https://www.python.org/downloads/). Ensure you check "Add Python to PATH" during installation.
*   **Telegram Bot Token:** Create a new bot by talking to `@BotFather` on Telegram. You will receive an API token.
*   **Whitelisted Telegram Chat ID:** Find your Telegram chat ID. You can use bots like `@userinfobot` to get your chat ID.
*   **LLM API Key:** Obtain an API key for your chosen LLM provider (e.g., OpenAI API key for `gpt-4o-mini` or Anthropic API key for `claude-3-haiku`).

### 2. Project Setup

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <repository_url>
    cd telegram_laptop_assistant
    ```
    (If you downloaded, navigate to the project directory.)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    # source venv/bin/activate # On Linux/macOS
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  **Create `.env` file:** Copy the provided `.env.example` to a new file named `.env` in the root of the project directory.
    ```bash
    copy .env.example .env
    ```

2.  **Edit `.env`:** Open the `.env` file and fill in your credentials and desired settings:
    ```ini
    # Telegram Bot API Token (from BotFather)
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"

    # Your whitelisted Telegram Chat ID (integer)
    WHITELISTED_CHAT_ID=123456789 # Replace with your actual chat ID

    # Primary LLM Provider: "google", "openai", "anthropic", "openrouter"
    PRIMARY_LLM_PROVIDER="google"

    # Primary LLM API Key
    PRIMARY_LLM_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"

    # Primary LLM Model (e.g., gemini-pro for Google)
    PRIMARY_LLM_MODEL="gemini-pro"

    # Fallback LLM Provider: "google", "openai", "anthropic", "openrouter" (optional)
    FALLBACK_LLM_PROVIDER="openrouter"

    # Fallback LLM API Key (optional)
    FALLBACK_LLM_API_KEY="YOUR_OPENROUTER_API_KEY"

    # Fallback LLM Model (e.g., google/gemini-pro for OpenRouter)
    FALLBACK_LLM_MODEL="google/gemini-pro"

    # ... other settings (power check intervals, logging) can be adjusted as needed
    ```

### 4. Running the Assistant

To run the assistant, ensure your virtual environment is activated and execute the `main.py` file:

```bash
python src/main.py
```

### 5. Auto-start on Windows (Only while charging)

To make the assistant start automatically when your laptop boots and respect the "only while charging" rule, you can use Windows Task Scheduler:

1.  **Open Task Scheduler:** Search for "Task Scheduler" in the Windows Start menu.
2.  **Create Basic Task:** In the right-hand pane, click "Create Basic Task...".
3.  **Name and Description:** Give it a name (e.g., "Telegram AI Assistant") and a description.
4.  **Trigger:** Select "When the computer starts".
5.  **Action:** Select "Start a program".
6.  **Program/script:** Browse to your Python executable within your virtual environment. For example: `C:\path\to\your\project\venv\Scripts\python.exe`
7.  **Add arguments (optional):** `src/main.py`
8.  **Start in (optional):** Enter the path to your project's root directory (e.g., `C:\path\to\your\project\telegram_laptop_assistant`).
9.  **Finish:** Click "Finish".
10. **Adjust Task Properties:** Double-click the newly created task to open its properties.
    *   Go to the **Conditions** tab.
    *   Check "Start only if the computer is on AC power".
    *   (Optional) Check "Stop if the computer switches to battery power" and "Start on a network connection" if desired.
    *   Go to the **Settings** tab.
    *   Consider checking "Run task as soon as possible after a scheduled start is missed" if you want it to start even if the laptop was on battery at boot.
    *   Click "OK".

This setup ensures the Python script runs at startup, and the `main.py` logic (specifically the `is_charging` check and `listener.stop()`/`listener.start()` calls) will handle pausing/resuming the Telegram listener based on the AC power status.

## How to Add a New Command

Adding new commands to your assistant is designed to be straightforward:

1.  **Define the Handler in `src/executor.py`:**
    *   Open `src/executor.py`.
    *   Add a new static method to the `CommandExecutor` class. This method will contain the logic for your new command.
    *   It should accept a `params` dictionary as an argument.
    *   Example:
        ```python
        @staticmethod
        def new_custom_command(params):
            # Your command logic here
            message = params.get("message", "Default message")
            logger.info(f"Executing new custom command with message: {message}")
            return f"Custom command executed with: {message}"
        ```

2.  **Register the Handler:**
    *   In the `CommandExecutor.execute` method, add your new command to the `handlers` dictionary.
    *   The key should be the command name (e.g., `"new_custom_command"`), and the value should be a reference to your new static method (e.g., `cls.new_custom_command`).
    *   Example:
        ```python
        handlers = {
            # ... existing commands ...
            "new_custom_command": cls.new_custom_command,
        }
        ```

3.  **Update LLM Prompt (if necessary):**
    *   If your new command needs to be recognized by the LLM, you might need to update the prompt in `src/classifier.py` to include it in the list of possible actions.
    *   Modify the `prompt` string in the `llm_check` method to mention your new command and its expected parameters.

4.  **Test Your New Command:**
    *   Run the assistant and send a Telegram message that should trigger your new command.
    *   Check the logs (`assistant.log`) for execution details and Telegram for confirmation messages.

## Test Table

Here are some example messages and their expected classifications and actions:

| Message Text                                     | Expected Classification | Expected Action / Parameters                                   |
| :----------------------------------------------- | :---------------------- | :------------------------------------------------------------- |
| Hi there!                                        | CASUAL                  | Log only                                                       |
| How are you doing today?                         | CASUAL                  | Log only                                                       |
| open chrome and search in youtube lofi music     | COMMAND                 | `open_browser_search`, `{"query": "lofi music"}`             |
| go to sleep                                      | COMMAND                 | `system_sleep`                                                 |
| shutdown the laptop                              | COMMAND                 | `system_shutdown`                                              |
| lock the screen                                  | COMMAND                 | `lock_screen`                                                  |
| open notepad                                     | COMMAND                 | `open_app`, `{"app_name": "notepad"}`                        |
| close chrome                                     | COMMAND                 | `close_app`, `{"app_name": "chrome"}`                        |
| please open the calculator app                   | COMMAND                 | `open_app`, `{"app_name": "calculator"}`                     |
| what's the weather like?                         | CASUAL (LLM fallback)   | Log only (unless a weather command is added)                   |

## Quality Bar

*   Runs unmodified on Python 3.10+ on Windows, given correct config values.
*   Handles gracefully: no internet, Telegram API down, LLM API down, missing config keys — degrade/retry, never hard-crash.
*   Dependency footprint: standard library + `psutil` + one Telegram SDK + one LLM SDK. Nothing heavier.

## Dependencies

See `requirements.txt` for a full list of Python dependencies.
