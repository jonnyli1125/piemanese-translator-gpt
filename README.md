# Piemanese Translator GPT

OpenAI GPT wrapper for translating Piemanese to English. Continuation of [piemanese-translator](https://github.com/jonnyli1125/piemanese-translator).

## Usage

Set the environment variables:
```bash
export DISCORD_API_TOKEN=...
export DISCORD_USER_IDS=...  # comma-separated list of user ids
export OPENAI_API_KEY=...
export OPENAI_GPT_PROMPT_FORMAT=...  # path to text file or a text string
```

Start the bot:
```bash
python3 bot.py
```

## Deploy to GCP

Build and push image:
```bash
gcloud builds submit --pack image=gcr.io/piemanese-translator/bot-job
```

Then, upload prompt to `~/prompts/prompt.txt`, add volume mounts, and set environment variables accordingly.

Finally, restart the VM instance.
