# essential
import os
import discord
import random
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests
import datetime
import os.path
from dateutil import parser
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Special permissions to be able to use the bot
#intents = discord.Intents.default()
intents = discord.Intents.all()
intents.members = True
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.guilds = True
client = commands.Bot(command_prefix='%', intents=intents)  # bot object


# global random messages variables
lastTwoRandomMessages = [
    "Gosto mais da Ferb do que Phineas", "SAEComp melhor SA"]

# global roles variables
random_emojis = ["🖐", "👌", "🤑", "🍕", "🍣",
                 "🍷", "🥕", "✈", "🎈", "🎃", "🖖", "👋", "🙏"]
escolher_game_roles_id = 824803055345336330
escolher_ano_channel_id = 812769812861157410
fora_da_ec_message_id = 827227120035954758

WELCOME_CHANNEL_ID = 812783690773037107


escolher_ano_emojis = [
    "<:017_ano:938881567823110204>",
    "<:018_ano:938881567823122452>",
    "<:019_ano:938881567927971910>",
    "<:020_ano:938881567781191762>",
    "<:021_ano:938881567579852811>",
    "<:022_ano:938881567969935420>",
    "<:023_ano:1068282529494343730>",
    "<:nenhum_ano:938881567810527282>"
]

anos_roles_id = [
    "812786410184245338",   # 017
    "812767425942650880",   # 018
    "812767411526303794",   # 019
    "812767373521715250",   # 020
    "812767353820676106",   # 021
    "938864548570611712",   # 022
    "1068282004401049692",  # 023
    "827227117866975262"    # Nao eng comper
]

anos_map_from_roles = {
    escolher_ano_emojis[0]: anos_roles_id[0],
    escolher_ano_emojis[1]: anos_roles_id[1],
    escolher_ano_emojis[2]: anos_roles_id[2],
    escolher_ano_emojis[3]: anos_roles_id[3],
    escolher_ano_emojis[4]: anos_roles_id[4],
    escolher_ano_emojis[5]: anos_roles_id[5],
    escolher_ano_emojis[6]: anos_roles_id[6],
    escolher_ano_emojis[7]: anos_roles_id[7]
}





@client.event
async def on_member_join(member):

    new_member_private_message = f""" 
Bem vinde ao discord oficial da Engenharia de Computação da USP de São Carlos!

Lembre-se de escolher o seu ano no canal {client.get_channel(escolher_ano_channel_id).mention}
    """

    # Mandar mensagem pro membro falando pra escolher as roles no channel de roles
    try:
        await member.send(new_member_private_message)
        print("Mandei mensagem no privado do membro")
    except:
        print("O novo membro nao deixa mandar mensagem no privado :(")

    # Pegar o channel de novos participantes
    new_member_channel = client.get_channel(WELCOME_CHANNEL_ID)
    new_member_message = member.mention + \
        " seja bem vinde!\t<:perry:824019135880364053> <:p_heart:830601667937435679>"

    await new_member_channel.send(new_member_message)


@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)

    if channel.id == escolher_game_roles_id:  # roles related
        guild = client.get_guild(payload.guild_id)
        all_the_roles = await guild.fetch_roles()
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        embeds = message.embeds
        role_name = embeds[0].title
        for role in all_the_roles:
            if role.name.lower() == role_name.lower():
                role_storage = role

        await member.add_roles(role_storage)
        return

    if channel.id == escolher_ano_channel_id:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        # Pegar a reacao que o usuario colocou
        role_choosed = payload.emoji
        emoji_parsed = f"<:{role_choosed.name}:{role_choosed.id}>"
        # Verificar se foi algum emoji que nao é permitido
        if (emoji_parsed not in escolher_ano_emojis):
            # Remover emoji
            print("uepa entrei aqui")
            await message.clear_reaction(payload.emoji)
            return

        new_role_from_reaction_id = anos_map_from_roles[emoji_parsed]

        # Adicionar a role nas roles do usuario
        role_from_id = guild.get_role(int(new_role_from_reaction_id))

        await member.add_roles(role_from_id)
        return


# -------------------------------------------------------------------------------------------
@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)

    # role related
    if channel.id == escolher_game_roles_id:
        guild = client.get_guild(payload.guild_id)
        all_the_roles = await guild.fetch_roles()
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        embeds = message.embeds
        role_name = embeds[0].title
        for role in all_the_roles:
            if role.name.lower() == role_name.lower():
                role_storage = role

        await member.remove_roles(role_storage)

    if channel.id == escolher_ano_channel_id:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        # Pegar a reacao que o usuario colocou
        role_choosed = payload.emoji
        emoji_parsed = f"<:{role_choosed.name}:{role_choosed.id}>"

        if (emoji_parsed not in escolher_ano_emojis):
            return

        new_role_from_reaction_id = anos_map_from_roles[emoji_parsed]

        # Adicionar a role nas roles do usuario
        role_from_id = guild.get_role(int(new_role_from_reaction_id))

        await member.remove_roles(role_from_id)


# -------------------------------------------------------------------------------------------

@client.command(name="role")
async def RoleManipulation(ctx, *, args):
    guild = ctx.guild

    splitted = args.split(' ')

    if splitted[0] == "add":
        splitted.pop(0)

        if (len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)

        # flag = False
        # for role in ctx.author.roles:
        #     if role.name == "SaeComp": flag = True
        # if(flag == True):

        for role in guild.roles:
            if role_name.lower() == "saecomp":
                response = "Essa role esta indisponível!"
                await ctx.channel.send(response)
                return
            if role_name.lower() == "saecomp_rh":
                response = "Essa role esta indisponível!"
                await ctx.channel.send(response)
                return
            if role_name.lower() == role.name.lower():
                response = "Essa role já existe!"
                await ctx.channel.send(response)
                return

        # Create the role with the name args
        color = random.randint(0, 16777215)
        await guild.create_role(name=role_name, colour=color)

        response_at_channel = "Role criada!"
        await ctx.channel.send(response_at_channel)

        channel = client.get_channel(escolher_game_roles_id)
        embed = discord.Embed(title=str(
            role_name.upper()), description="Reaja a esta mensagem para ganhar a role")
        message = await channel.send(embed=embed)
        await message.add_reaction(random.choice(random_emojis))

    # -------------------------------------------------------------------------------------------

    # remove role if member is from SaeComp
    elif splitted[0] == "remove":
        splitted.pop(0)

        if (len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)

        flag = False
        for role in ctx.author.roles:
            if role.name == "SaeComp" or role.name == "SAEComp_RH":
                flag = True

        if (flag == True):
            for role in guild.roles:
                if role.name.lower() == role_name.lower():
                    channel = client.get_channel(escolher_game_roles_id)
                    async for message in channel.history(limit=1000):
                        embeds = message.embeds
                        for embed in embeds:
                            if embed.title.lower() == role_name.lower():
                                await message.delete()

                    response = "Role removida"
                    await role.delete()
                    await ctx.channel.send(response)
                    return

            response = "Role inexistente"
            await ctx.channel.send(response)

    # -------------------------------------------------------------------------------------------
    # list all the members from a role
    elif splitted[0] == "list":
        splitted.pop(0)
        if (len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)
        flag = False
        for role in guild.roles:
            if role_name.lower() == role.name.lower():
                flag = True
                role_id = role.id

        if (flag == True):
            # get all role memebers
            roleChosen = guild.get_role(role_id)
            role_members = roleChosen.members
            description = str()
            for member in role_members:
                if member.nick == None:
                    description += member.name + '\n'
                else:
                    description += member.nick + '\n'
            title = "Membros de " + str(roleChosen.name)
            embed = discord.Embed(title=title, description=description)
            await ctx.channel.send(embed=embed)
        else:
            response = "Role inexistente"
            await ctx.channel.send(response)

    # role help format
    elif splitted[0] == "help":
        response = "Digite %role add [nome]: para adicionar uma role nova\nDigite %role list [role]: para listar todos os membros desta role"
        await ctx.channel.send(response)

    # -------------------------------------------------------------------------------------------

    else:
        response = "Formato errado\nDigite %role help"
        await ctx.channel.send(response)


@client.event
async def on_message(ctx):

    if ctx.author == client.user:
        return

    # if ctx.content.lower() == 'uepa':
    #     response = "Selecione uma das opções abaixo para definir seu ano de ingresso: \n\n Você pode escolher mais de um ano \n\n Caso o seu ano não esteja presente na lista abaixo mande mensagem para alguem da "

    #     # mencionar saecomp
    #     role_storage = None
    #     for role in ctx.author.roles:
    #         if role.name == "SaeComp":
    #             role_storage = role

    #     response += f"{role_storage.mention} \n\n"

    #     for i, emoji in enumerate(escolher_ano_emojis):
    #         if (i == len(escolher_ano_emojis)-1):
    #             break

    #         response += f"  {emoji}  "

    #     response += "\n\n"

    #     last_emoji = escolher_ano_emojis[-1]

    #     response += f"{last_emoji} Outro curso."

    #     message = await ctx.channel.send(response)
    #     for emoji in escolher_ano_emojis:
    #         await message.add_reaction(emoji)

    # greetings
    if ctx.content.lower() == "oi perry":
        if ctx.author.nick == None:
            response = "Oi " + str(ctx.author.name) + '!'
        else:
            response = "Oi " + str(ctx.author.nick) + '!'
        await ctx.channel.send(response)

    if ctx.content.lower() == "bcc":
         await ctx.channel.send("#XUPABCC!")

    if ctx.content.lower() == "federal":
        await ctx.channel.send("#XUPAFEDERAL!")

    if ctx.content.lower() == "jean":
        await ctx.channel.send("يساعد")

    if ctx.content.lower() == "ku":
        await ctx.channel.send("Umedar (Verbo Transitivo Direto):\nDefinição: Umedar é um termo utilizado para descrever a ausência ou falta às reuniões da Diretoria Técnica da Saecomp (Secretaria Acadêmica da Engenharia da Computação). O termo é específico para o contexto dessa organização e é amplamente utilizado pelos membros para se referir à situação em que um indivíduo não comparece a uma reunião importante.")
    
    if ctx.content.lower() == "homer":
        await ctx.channel.send("Eu te amo Homer!!")


    await client.process_commands(ctx)

async def Notion_Bot():
    await client.wait_until_ready()
    while True:
        print("Starting NotionBot. Horário: ", datetime.datetime.now().strftime("%H:%Mh"))
        TOKEN_NOTION = os.environ["TOKEN_NOTION"]

        databaseId = '7300faddb03f45a0b6932149d66510d5'

        headers = {
            "Authorization": "Bearer " + TOKEN_NOTION,
            "Notion-Version": "2022-06-28",
            "content-type": "application/json"
        }

        readUrl = f"https://api.notion.com/v1/databases/{databaseId}/query"
        res = requests.request("POST", readUrl, headers=headers)
        dados = res.json()["results"]
        for properties in dados:
            Checkbox = properties["properties"]["Checkbox"]["checkbox"]
            if Checkbox == False:
                nome_do_projeto = properties["properties"]["Name"]["title"][0]["text"]["content"]
                if properties["properties"]["Descrição"]["rich_text"]:
                    descricao = properties["properties"]["Descrição"]["rich_text"][0]["text"]["content"]
                else:
                    descricao = "Não Especificado"
                Solicitante = properties["properties"]["Solicitante"]["created_by"]["name"]
                if properties["properties"]["Data de entrega"]["date"] is None:
                    Entrega = "Não especificado"
                else:
                    Entrega = str(properties["properties"]["Data de entrega"]["date"]["end"])
                if properties["properties"]["Diretoria"]["select"] is None:
                    diretoria = "Não especificado"
                else:
                    diretoria = str(properties["properties"]["Diretoria"]["select"]["name"])
                channel = client.get_channel(845049025018200075)
                await channel.send("Oi @diretoria\nTem uma nova nota no Notion! Vou te mandar os detalhes:")
                await channel.send("Nome do Projeto: " + nome_do_projeto + "\nDescrição do Projeto: " + descricao + "\nSolicitante: " + Solicitante + "\nDiretoria: " + diretoria + "\nData de Entrega: " + Entrega)
                page_id = properties["id"]
                update_url = f"https://api.notion.com/v1/pages/{page_id}"
                new_props = {
                    "Checkbox": {
                        "checkbox": True
                    }
                }
                update_data = {
                    "properties": new_props
                }
                requests.patch(update_url, headers=headers, json=update_data)
        await asyncio.sleep(900)


async def Calendar_Bot():
    await client.wait_until_ready()
    channel = client.get_channel(1108540671092064276)
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    TOKEN_GOOGLE =  eval(os.environ.get('TOKEN_GOOGLE'))
    creds = Credentials.from_authorized_user_info(TOKEN_GOOGLE , SCOPES)
    try:
        print("Starting Calendar Bot. Horário: ", datetime.datetime.now().strftime("%H:%Mh"))
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        calendars = service.calendarList().list().execute()
        for calendar in calendars['items']:
            calendar_id = calendar['id']
            calendar_name = calendar['summary']
            if calendar_name != "Holidays in Brazil" and calendar_name != "Aniversários":
                events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                                    maxResults=10, singleEvents=True,
                                                    orderBy='startTime').execute()
                events = events_result.get('items', [])

                # Lista para armazenar os eventos
                eventos_hoje = []

                # Percorre os eventos e verifica se a data é a de hoje
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    data = parser.parse(start)
                    if data.date() == datetime.date.today():
                        # Armazena as informações do evento na lista
                        evento_info = {
                            'horario': data.strftime('%H:%M'),
                            'summary': event['summary'],
                            'description': ''
                        }
                        if 'description' in event:
                            description = event['description']
                            soup = BeautifulSoup(description, 'html.parser')
                            description = soup.get_text()
                            evento_info['description'] = description
                        eventos_hoje.append(evento_info)

                # Imprime os eventos armazenados
                if eventos_hoje:
                    channel = client.get_channel(845046607618506772)
                    await channel.send(f'Bom dia, @everyone! Acabei de ver que temos compromissos hoje na seguinte Agenda {calendar_name}. \nAqui estao os detalhes do(s) evento(s):')
                    for evento in eventos_hoje:
                        await channel.send("Horário: " + evento['horario'] + "h   " + evento['summary'] + "\nDescrição/Local: " + evento['description'])
    

    except HttpError as error:
        print('An error occurred: %s' % error)


SECRET_TOKEN = None
try:
    SECRET_TOKEN = os.environ["TOKEN"]
    if (SECRET_TOKEN == None):
        raise Exception("Erro ao ler o conteudo do .env para o DATABASE_URL")
except:
    raise Exception("Erro ao ler o conteudo do .env para o DATABASE_URL")

async def agendar_calendario():
    while True:
        # Aguardar até que seja 8h da manhã
        agora = datetime.datetime.now()
        proxima_task = agora.replace(hour=11, minute=0, second=0, microsecond=0)
        if agora > proxima_task:
            # Se já passou das 8h hoje, agendar para amanhã
            proxima_task += datetime.timedelta(days=1)
        espera = (proxima_task - agora).total_seconds()
        await asyncio.sleep(espera)
        # Executar a tarefa diária
        asyncio.create_task(Calendar_Bot())
        await asyncio.sleep(1200)

# -------------------------------------------------------------------------------------------
# When the bot logs in
@client.event
async def on_ready():
    print("logged on as ", client.user.name)
    asyncio.create_task(Notion_Bot())
    channel = client.get_channel(1108540671092064276)
    asyncio.create_task(agendar_calendario())
        

client.run(SECRET_TOKEN)
