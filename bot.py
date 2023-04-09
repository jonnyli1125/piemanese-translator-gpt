import os
import asyncio
import discord
import openai

class PiemaneseTranslatorClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pi_user_ids = [int(x) for x in os.environ['DISCORD_USER_IDS'].split(',')]
        self.msg_queue = []
        self.delay = 5
        self.gpt_model = 'text-davinci-003'
        self.gpt_prompt = os.environ['OPENAI_GPT_PROMPT_FORMAT']

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, msg):
        if msg.author.id == self.user.id:
            return
        if not msg.content:
            return
        if msg.guild and msg.author.id not in self.pi_user_ids:
            return
        self.msg_queue.append(msg)
        current_len = len(self.msg_queue)
        async with msg.channel.typing():
            await asyncio.sleep(self.delay)
            if len(self.msg_queue) > current_len:
                return
            msg_batch_text = '\n'.join(x.clean_content for x in self.msg_queue)
            msg_batch_translated = self.gpt(msg_batch_text)
            print(f'{msg.author}:\n{msg_batch_text}')
            print(f'{self.user}:\n{msg_batch_translated}')
            await msg.channel.send(msg_batch_translated)
            self.msg_queue.clear()

    def gpt(self, text):
        prompt = self.gpt_prompt.format(text)
        completion = openai.Completion.create(model=self.gpt_model, prompt=prompt, max_tokens=256, temperature=0.1)
        return completion.choices[0].text.strip()

def main():
    assert 'DISCORD_API_TOKEN' in os.environ
    assert 'DISCORD_USER_IDS' in os.environ
    assert 'OPENAI_API_KEY' in os.environ
    assert 'OPENAI_GPT_PROMPT_FORMAT' in os.environ

    intents = discord.Intents.default()
    intents.message_content = True
    client = PiemaneseTranslatorClient(intents=intents)
    client.run(os.environ['DISCORD_API_TOKEN'])

if __name__ == '__main__':
    main()
