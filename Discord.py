import discord
from discord.ext import commands

# Configuration
TOKEN = "MTE2NTkzNzE5NjI5Mzk0NzQwMg.GeaYH_.dnBuxo3x_AmZmiqzqEnk1yQLGLfGmX-kKAKT3Y"
PREFIX = "!"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Événement de démarrage
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user.name} ({bot.user.id})")

# Commande "ping"
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Commande "hello"
@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

# Lancement du bot
bot.run(TOKEN)
