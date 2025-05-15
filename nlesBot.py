import os
from dotenv import load_dotenv
from openai import OpenAI
import discord
from discord.ext import commands
import requests

load_dotenv(".env")
api_key = os.getenv("OPENAI_API_KEY")
client_openai = OpenAI(api_key=api_key)

DISCORD_BOT_KEY = os.getenv("DISCORD_BOT_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class ButtonView(discord.ui.View):
    @discord.ui.button(label="Bible AI!", style=discord.ButtonStyle.primary, custom_id="AI_Button")
    async def AI_Button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("**Ask AI about the Bible** \n(*It won't entertain non-Bible questions*)", ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            message = await bot.wait_for("message", check=check, timeout=20)
            completion = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": ("You are a helpful assistant that answers questions only about the Christian Bible." 
                                                   "Make your the most concise possible."
                                                   "If the question is unrelated to the Bible, respond with: 'I only entertain questions about the **Bible**.")},
                    {"role": "user", "content": message.content}
                ]
            )
            output = completion.choices[0].message.content
            await interaction.followup.send(output)
        except Exception as e:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)

    @discord.ui.button(label="Get Random Verse", style=discord.ButtonStyle.secondary, custom_id="random_button")
    async def random_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        url_random = "https://bible-api.com/?random=verse"
        response_random = requests.get(url_random)
        if response_random.status_code == 200:
            data = response_random.json()
            verse_reference = f"**{data['reference']}**"
            verse_text = data['text']
            await interaction.response.send_message(f"{verse_reference}\n{verse_text}")
        else:
            await interaction.response.send_message("Error retrieving a random verse. Please try again later.")

    @discord.ui.button(label="Enter Specific Verse", style=discord.ButtonStyle.secondary, custom_id="specific_verse_button")
    async def specific_verse_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please type the verse you'd like to retrieve (e.g., John 3:16).", ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            message = await bot.wait_for("message", check=check, timeout=20)
            verse = message.content.strip()
            url = f"https://bible-api.com/{verse}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'text' in data:
                    verse_reference = f"**{data['reference']}**"
                    verse_text = data['text']
                    await interaction.followup.send(f"{verse_reference}\n{verse_text}")
                else:
                    await interaction.followup.send(f"Sorry, the verse '{verse}' does not exist or could not be found.", ephemeral=True)
            else:
                await interaction.followup.send("Sorry, the verse could not be found. Please try again.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('+help'):
        embed = discord.Embed(title="Bot Commands", color=0xFF0000)
        embed.add_field(name="Instructions", value="Type '+bot' to access the features", inline=False)
        embed.add_field(name="Random Button", value="Click the button to get a random verse.", inline=False)
        embed.add_field(name="Specific Verse Button", value="Click the button and type the verse you want.", inline=False)
        await message.channel.send(embed=embed)

    elif message.content.startswith('+bot'):
        view = ButtonView()
        await message.channel .send("Click a button!", view=view, ephemeral=True)

    elif message.content.startswith('+update'):
        await message.channel.send("UPDATE! Instead of typing out the commands, just type '+bot' and it will provide buttons for the features!")

bot.run(DISCORD_BOT_KEY)
