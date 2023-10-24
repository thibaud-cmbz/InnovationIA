import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import openai

load_dotenv()
intents = discord.Intents.all()
token = os.environ.get("MY_TOKEN")
openai_key = os.environ.get("OPENAPI_KEY")
openai.api_key = openai_key

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_reaction_add(reaction, user):
    channel_name = "aventure"
    channel = discord.utils.get(reaction.message.guild.channels, name=channel_name)
    if user == bot.user:
        return
    if reaction.message.content == "Réagissez a l'émoji pour commencer le jeu.":
        role = discord.utils.get(reaction.message.guild.roles, name='aventure')
        if role:
            await user.add_roles(role)
            if channel:
                await channel.send(f"{user.mention}, Bienvenue dans l'aventure")
            else:
                print(f"Channel '{channel_name}' non trouvé.")
        else:
            print("Rôle 'aventure' introuvable.")

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send("Pong!")

@bot.event
async def on_message(message):
    # Ne faites rien si le bot est l'auteur du message
    if message.author == bot.user:
        return
    # Si le message contient "remove"
    if "remove" in message.content.lower():
        role = discord.utils.get(message.guild.roles, name='aventure')
        # Si le rôle existe et que l'utilisateur l'a
        if role and role in message.author.roles:
            await message.author.remove_roles(role)
            await message.channel.send(f"{message.author.mention}, le rôle 'aventure' vous a été retiré.")
        elif role:
            await message.channel.send(f"{message.author.mention}, vous n'avez pas le rôle 'aventure'.")
    # N'oubliez pas de traiter les autres commandes également
    await bot.process_commands(message)


@bot.command(name='presentation')
async def presentation(ctx):
    await ctx.send("Bonjour, je suis un bot discord créé pour le serveur discord de Neopolis.")

@bot.command(name='start')
async def game(ctx):
    message = await ctx.send("Réagissez a l'émoji pour commencer le jeu.")
    # Vous pouvez remplacer l'émoji ci-dessous par celui de votre choix
    await message.add_reaction('🚀')

@bot.command(name='gpt')
async def gpt(ctx):
    # Faites une demande à l'API OpenAI
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un Policier nommé Fabrice et tu as 10 ans d'experice, réponds à la question suivante, s'il te manque des informations tels que des noms ou des dates, invente les :"},
                {"role": "user", "content": "Présente toi"}
            ]
        )
        print(completion.choices[0].message.content.strip())

    except Exception as e:
        await ctx.send(f"Erreur lors de la requête à OpenAI : {e}")

bot.run(token)
