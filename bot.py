import os
import asyncio
import discord
from openai import OpenAI
import re
import logging

class PiemaneseTranslatorClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pi_user_ids = [int(x) for x in os.environ['DISCORD_USER_IDS'].split(',')]
        self.msg_queue = []
        self.delay = 10
        self.openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.gpt_model = 'gpt-4'
        self.gpt_prompt = os.environ['OPENAI_GPT_PROMPT_FORMAT']
        if os.path.isfile(self.gpt_prompt):
            with open(self.gpt_prompt, 'r') as f:
                self.gpt_prompt = ''.join(f.readlines())
        self.ignore_exprs = []
        if os.path.isfile('ignore.txt'):
            with open('ignore.txt', 'r') as f:
                self.ignore_exprs = [re.compile(line.strip()) for line in f]
        self.log = logging.getLogger('discord.piemanese-translator')

    async def on_ready(self):
        self.log.info('Logged in as %s', self.user)

    async def on_message(self, msg):
        if msg.author.id == self.user.id:
            return
        if not msg.content:
            return
        if msg.guild and msg.author.id not in self.pi_user_ids:
            return
        for expr in self.ignore_exprs:
            if expr.match(msg.clean_content):
                return
        self.msg_queue.append(msg)
        current_len = len(self.msg_queue)
        async with msg.channel.typing():
            await asyncio.sleep(self.delay)
            if len(self.msg_queue) > current_len:
                return
        msg_batch_text = [x.clean_content for x in self.msg_queue]
        msg_batch_translated = self.gpt(msg_batch_text)
        self.log.info('%s: %s', msg.author, '\n'.join(msg_batch_text))
        self.log.info('%s: %s', self.user, msg_batch_translated)
        await msg.channel.send(msg_batch_translated)
        self.msg_queue.clear()

    def gpt(self, texts):
        messages = [
                {'role': 'system', 'content': self.gpt_prompt},
                {'role': 'user', 'content': '\n'.join(texts)}
            ]
        completion = self.openai.chat.completions.create(model=self.gpt_model, messages=messages, temperature=0.1)
        return completion.choices[0].message.content.strip()

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
