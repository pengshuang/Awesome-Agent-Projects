# Quick Start

This unified quick start guide provides the minimal steps to get any subproject in this repository running.

## 1. Clone the repository

```bash
git clone https://github.com/pengshuang/Awesome-Agent-Projects.git
cd Awesome-Agent-Projects
```

## 2. Choose a subproject

Available projects:
- `academic-paper-qa`
- `ai-data-analyst`
- `interview-coach`

Enter the chosen project directory, for example:

```bash
cd academic-paper-qa
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy the example env file and edit it to add your LLM API keys and other settings:

```bash
cp .env.example .env
# Edit .env and fill in required variables (LLM_API_KEY, etc.)
```

## 5. Launch the app

Most projects provide simple start scripts or Python entrypoints. Example (academic-paper-qa):

```bash
./start_web_multi.sh    # Start multi-turn web UI
# or
python web_ui_multi_turn.py
```

Visit the local UI (if provided) in your browser (commonly `http://127.0.0.1:7860` or project-specific port).

## 6. Examples and troubleshooting

- For detailed usage, examples, developer docs and troubleshooting, open the subproject `docs/` folder or its README.
- If run-time issues occur, check `logs/` or console output for errors and verify `.env` values.

---

If you want, I can also shorten the per-project README quick-start sections to a single line linking to this file (I will do that next if you confirm).