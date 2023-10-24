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
    if reaction.emoji == '✅' and reaction.message.author == bot.user and discord.utils.get(user.roles, name='aventure') is None :
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
    try:
        completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Tu es un chatbot, réponds à la commande ping"},
                        {"role": "user", "content": "ping"},
                    ]
                )
        await ctx.send(f"{completion.choices[0].message.content.strip()})")
    except Exception as e:
        await ctx.send(f"Erreur lors de la requête à OpenAI : {e}")

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
    # N'oubliez pas de traiter les autres commandes également
    await bot.process_commands(message)


@bot.command(name='presentation')
async def presentation(ctx):
    await ctx.send("Bonjour, je suis un bot discord créé pour le serveur discord de Neopolis.")

def create_embed(title : str, description : str, img_url : str, color: str, fields: list):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    for i in range (0, len(fields), 2):
        embed.add_field(name=fields[i + 1], value=fields[i], inline=False)
    embed.set_image(url=img_url)
    return embed

@bot.command(name='start')
async def game(ctx):
    embed = create_embed("Partez a l'assaut de la NéoZone 51",
                "Réagissez a l'émoji pour commencer le jeu.",
                "https://media.istockphoto.com/id/1288575278/vector/grand-canyon-national-park-night-landscape-ufo-over-the-desert.jpg?s=612x612&w=0&k=20&c=qmecdaROppZIpRDWNs4DER4MRo2Y6WfKcqSgea6PRpU=",
                0x00ff00,
                ["✅", "Réagissez avec si vous voulez participer", "❌", "Réagissez avec si vous ne voulez pas participer"])
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

@bot.command(name='scenario')
async def scenario(ctx, step:str):
    # try:
    async with ctx.typing():
        try:
            int(step)
        except ValueError:
            await ctx.send("Le scenario doit être un nombre")
            return
        if (step not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]):
            await ctx.send("Le scenario doit être compris entre 1 et 10")
            return
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Maître du jeu, créez une situation où les joueurs sont aux abords de la Zone 51, le site militaire secret. Ils doivent réussir à pénétrer dans la zone sans se faire repérer par les gardes, survivre dans le désert et des animaux qui s'y trouve. Découpe le scenario en 10 étapes avec la 1ère étape l'arrivée dand le desert et la 10ème l'énigme devant la porte finale, décrive la situation numéro " + str(step) + " et le défis auxquels les joueurs sont confrontés.S'il te manque des informations comme des noms ou des dates, invente le. Soit le plus rp possible pour une immersion parfaite pour les joueurs, mais n'oublie pas que tu es le maître du jeu et que tu peux faire ce que tu veux. Je veux que tu t'adresse en disant vous aux joueurs, et je ne veux pas que tu expliques la situation de départ, juste le scénario actuel, limite ton message a 2000 caractères."},
                    {"role": "user", "content": "explique la situation et crée une situation de départ pour les joueurs"},
                ]
            )
            print("request done")
            await ctx.send(f"{completion.choices[0].message.content.strip()})")

        except Exception as e:
            await ctx.send(f"Erreur lors de la requête à OpenAI : {e}")

bot.run(token)
