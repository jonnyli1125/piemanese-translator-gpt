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
        self.model = 'gpt-4'
        self.prompt = self.get_prompt()
        self.ignore_exprs = []
        if os.path.isfile('ignore.txt'):
            with open('ignore.txt', 'r') as f:
                self.ignore_exprs = [re.compile(line.strip()) for line in f]
        self.log = logging.getLogger('discord.piemanese-translator')

    def get_prompt(self):
        prompt = os.environ['OPENAI_PROMPT']
        if os.path.isfile(prompt):
            with open(prompt, 'r') as f:
                return ''.join(f.readlines())
        else:
            return prompt

    async def on_ready(self):
        self.log.info('Logged in as %s', self.user)

    async def on_message(self, msg):
        text = msg.clean_content
        if msg.author.id == self.user.id:
            return
        if not text:
            return
        if text == '!reload':
            self.prompt = self.get_prompt()
            prompt = os.environ['OPENAI_PROMPT']
            await msg.channel.send(f'Prompt reloaded: {prompt}, isfile: {os.path.isfile(prompt)}')
            return
        if msg.guild and msg.author.id not in self.pi_user_ids:
            return
        for expr in self.ignore_exprs:
            if expr.match(text):
                return
        self.msg_queue.append(text)
        current_len = len(self.msg_queue)
        async with msg.channel.typing():
            await asyncio.sleep(self.delay)
        if not self.msg_queue or len(self.msg_queue) > current_len:
            return
        msg_batch_translated = self.gpt(self.msg_queue)
        self.log.info('%s: %s', msg.author, '\n'.join(self.msg_queue))
        self.log.info('%s: %s', self.user, msg_batch_translated)
        await msg.channel.send(msg_batch_translated)
        self.msg_queue.clear()

    def gpt(self, texts):
        messages = [
                {'role': 'system', 'content': self.prompt},
                {'role': 'user', 'content': ' '.join(texts)}
            ]
        completion = self.openai.chat.completions.create(model=self.model, messages=messages, temperature=0)
        return completion.choices[0].message.content.strip()

def main():
    assert 'DISCORD_API_TOKEN' in os.environ
    assert 'DISCORD_USER_IDS' in os.environ
    assert 'OPENAI_API_KEY' in os.environ
    assert 'OPENAI_PROMPT' in os.environ

    intents = discord.Intents.default()
    intents.message_content = True
    client = PiemaneseTranslatorClient(intents=intents)
    client.run(os.environ['DISCORD_API_TOKEN'])

if __name__ == '__main__':
    main()
