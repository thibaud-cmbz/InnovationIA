import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import openai
import asyncio
import random

load_dotenv()
intents = discord.Intents.all()
token = os.environ.get("MY_TOKEN")
openai_key = os.environ.get("OPENAPI_KEY")
openai.api_key = openai_key

bot = commands.Bot(command_prefix='!', intents=intents)
IS_RUNNING = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} with is running {IS_RUNNING}')

@bot.event
async def on_reaction_add(reaction, user):
    if IS_RUNNING:
        return
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
    if IS_RUNNING:
        return
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

async def remove_role(ctx, winners):
    role = discord.utils.get(ctx.guild.roles, name='aventure')
    for member in ctx.guild.members:
        if member.id in winners:
            continue
        if role in member.roles:
            await member.remove_roles(role)

async def choose_winners(most_liked_message):
    for reaction in most_liked_message.reactions:
        if (str(reaction.emoji) == "👍"):
            print("get users")
            users_id = [user.id async for user in reaction.users()]
            for el in users_id:
                print("id: ", el)
    return users_id

@bot.command(name='presentation')
async def presentation(ctx):
    if IS_RUNNING:
        return
    await ctx.send("Bonjour, je suis un bot discord créé pour le serveur discord de Neopolis.")

def create_embed(title : str, description : str, img_url : str, color: str, fields: list):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    for i in range (0, len(fields), 2):
        embed.add_field(name=fields[i + 1], value=fields[i], inline=False)
    if img_url != "":
        embed.set_image(url=img_url)
    return embed

async def send_with_embed(ctx, image_path):
    with open(image_path, 'rb') as f:
        picture = discord.File(f, filename="image.png")  # Vous pouvez changer le nom de fichier si nécessaire
        embed = create_embed("Partez a l'assaut de la NéoZone 51",
                "Réagissez a l'émoji pour commencer le jeu.",
                "attachment://image.png",
                0x00ff00,
                ["✅", "Réagissez avec si vous voulez participer", "❌", "Réagissez avec si vous ne voulez pas participer"])
    message = await ctx.send(file=picture, embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

@bot.command(name='start')
async def game(ctx):
    if IS_RUNNING:
        return
    await send_with_embed(ctx, "Assets/banner.png")

async def send_if_2000(ctx, message):
    if len(message) > 1998:
        while len(message) > 1998:
            await ctx.send("*" + message[:1998] + "*")
            message = message[1998:]
    else:
        await ctx.send("*" + message + "*")

@bot.command(name='scenario')
async def scenario(ctx):
    global IS_RUNNING
    if IS_RUNNING:
        return
    IS_RUNNING = True
    etapes = ["Traversée du desert pour arriver devant la base", "Persuader le militaire de nous laisser rentrer", "Escalader le grillage elecrifié", "Echapper aux serpents mutants ", "Ouvrir la dernière porte blindée"]
    response = ""
    LIVES = 3
    async with ctx.typing():
        try:
            for i in range(5):
                #explain context
                message = create_embed("**ETAPE N° " + str(i + 1) +"**", "", "", random.randint(0, 0xffffff), ["", "**Réagissez avec 👍  pour voter**", "", "**Attendez que j'explique la situation avant de proposer des messages**"])
                await ctx.send(embed=message)
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Tu es un aventurier qui nous suis dans notre aventure pour entrer dans la Zone 51, on doit faire face à des obstacles et les surmonter pour avancer dans l'aventure, on est à l'étape : " + etapes[i] + "explique la situation et présente-la-moi afin que je te dise comment on peut s'en sortir. Tu es libre d'inventer des noms mais ne pars pas trop loin et reste dans la réalité. Soit Role play, soit logique dans ce que tu dis et amuse-toi bien !"},
                        {"role": "user", "content": "explique la situation actuelle"},
                    ]
                )
                print("request done")
                response = completion.choices[0].message.content.strip()
                await send_if_2000(ctx, response)
                await ctx.send("**N'oubliez pas de réagir avec 👍 pour choisir la meilleure réponse**")
                await asyncio.sleep(90)
                print("take message")

                channel = bot.get_channel(int("1166346246655590533"))

                max_thumbs_up_count = -1
                most_liked_message = None

                async for message in channel.history(limit=50):
                    if message.author == bot.user:
                        break
                    for reaction in message.reactions:
                        if reaction.emoji == '👍' and reaction.count > max_thumbs_up_count:
                            max_thumbs_up_count = reaction.count
                            most_liked_message = message

                if most_liked_message:
                    print(f"Dernier message avec le plus de pouces levés: {most_liked_message.content}")
                    await ctx.send(f"Message choisi : {most_liked_message.content}")
                    # choose if response is good or not
                    winners = await choose_winners(most_liked_message)
                    await remove_role(ctx, winners)
                else:
                    print("no message detected")
                    message = create_embed("**VOUS AVEZ PERDU **", "**Raison : Aucun message n'a été voté**", "https://cdn5.vectorstock.com/i/1000x1000/58/14/game-over-play-again-in-cyber-noise-glitch-design-vector-22975814.jpg", 0xff0000, [])
                    await ctx.send(embed=message)
                    await remove_role(ctx, [])
                    IS_RUNNING = False
                    return
            message = create_embed("**VOUS AVEZ GAGNÉ **", "**Bravo, vous meritez une récompense !**", "https://as2.ftcdn.net/v2/jpg/05/61/11/27/1000_F_561112716_429m0h992ZhPzGYYzTM6smfk9H0KxO9a.jpg", 0x00ff00, [])
            await ctx.send(embed=message)
            await remove_role(ctx, [])
            IS_RUNNING = False

        except Exception as e:
            await ctx.send(f"Erreur lors de la requête à OpenAI : {e}")



bot.run(token)
