import discord, os, time, json, nacl, asyncio
from application import app, parseResponse, writeInfo, removeInfo, doesUserExits, getInfoFromUser, getInfoFromAllUsers
from linkss import getHelp, getLinks, getHino
from secret_token import TOKEN
from getextra import extras_name, extras_image_name, extras_description
from listafuvest import runScrapCheck
from threading import Thread
from discord.ext import tasks



async def run():
    flag = False
    while flag == False:
        flag, filename = runScrapCheck()
        if(flag == True):
            await client.sendFiles(filename)

        time.sleep(5)


def keep_alive():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
    loop.close()

class MyClient(discord.Client):
    async def on_ready(self):
        print("logged on as ", self.user)


    @tasks.loop(seconds=30)
    async def sendFiles(self):
        flag = False
        while flag == False:
            flag, filename = runScrapCheck()
            if(flag == True):
                channel = client.get_channel(821889877644804106)
                response = "!!Saiu a lista de chamada!!"
                await channel.send(response)
                await channel.send(file=discord.File(filename))
                await channel.send(file=discord.File("names.txt"))


    # @tasks.loop(seconds=30)
    # async def sendFiles(self, filename):
    #     channel = client.get_channel(821889877644804106)
    #     response = "!!Saiu a lista de chamada!!"
    #     await channel.send(response)
    #     await channel.send(file=discord.File(filename))
    #     await channel.send(file=discord.File("names.txt"))


    async def on_message(self, message):
        if message.author == self.user:
            return
        
        #greetings
        if message.content.lower() == "oi perry":
            if message.author.nick == None:
                response = "oi " + str(message.author.name)
            else:
                response = "oi " + str(message.author.nick)
    
            await message.channel.send(response)

        #handle usernames from different platforms and stores them
        if message.content.startswith("*") and message.content.lower() != "*remover" and message.channel.name == "🔭user-de-jogo" and ":" in message.content:
            get_message = message.content
            flag, content = app(get_message, message.author)
            if(flag == 0):
                await message.channel.send(content)
            else:
                response = parseResponse(content, message.author)
                await message.channel.send(response)
                writeInfo(content, message.author)

        #remove a requested username from a discord member
        if message.content.lower() == "*remover" and message.channel.name == "🔭user-de-jogo":
            removeInfo(message.author)
            response = "Dados Removidos " + message.author.mention
            await message.channel.send(response)

        #get information from a certain member. only saecomp members can do this.
        if message.content.startswith('%') and message.content.lower() != "%getall":
            user = message.content.replace('%' , '')
            flag, user = doesUserExits(user)
            if (flag == True):
                response = getInfoFromUser(user)
                await message.channel.send(response)
            else:
                response = "Esse usuário não existe nos arquivos, ele provavelmente não fez ou apagou.\n"
                await message.channel.send(response)

        #get info from all users
        if message.content.lower() == "%getall" and message.channel.name == "info-users":
            flag = False
            for role in message.author.roles:
                if role.name =="SaeComp":
                    flag = True
            
            if(flag == True):
                getInfoFromAllUsers()
                await message.channel.send(file=discord.File("users/getAllInfo.txt"))

        if message.content.lower() == "bcc":
            await message.channel.send("#XUPABCC")

        if message.content.lower() == "federal":
            await message.channel.send("#XUPAFEDERAL")

        if message.content.lower() == "*help":
            response = getHelp()
            embed = discord.Embed(title="Comandos" , description=response)
            await message.channel.send(embed=embed)

        if message.content.lower() == '*links':
            response = getLinks()
            embed = discord.Embed(title="🔗 Links úteis:" , description=response)
            await message.channel.send(response)

        if message.content.lower() == "*hino":
            response = getHino()
            await message.channel.send(response)


        if message.content.lower() == "%get debugg json" and message.channel.name == "info-users":
            flag = False
            for role in message.author.roles:
                if role.name == "SaeComp":
                    flag = True
            if(flag == True):
                await message.channel.send(file=discord.File("users/usersinfo.json"))

        if message.content.lower() == "%send extras" and message.channel.name == "extras" and message.author.name == "Franreno":
            for name,desc,img_name in zip(extras_name, extras_description, extras_image_name):
                embed = discord.Embed(title=name, description=desc)
                img_path = "extras/imgs/" + str(img_name)
                file = discord.File(img_path)
                await message.channel.send(embed=embed, file=file)

        if message.content.lower() == "%send welcome" and message.channel.name == "bem-vindx" and message.author.name == "Franreno":
            from welcome import welcome_image_names, welcome_titles, welcome_topics

            for name, topics, img_name in zip(welcome_titles, welcome_topics, welcome_image_names):
                embed = discord.Embed(title=name, description=topics)
                img_path = "imgs/" + str(img_name)
                file = discord.File(img_path)
                await message.channel.send(embed=embed, file=file)
            
        if message.content.lower() == "%send curso" and message.channel.name == "curso" and message.author.name == "Franreno":
            from curso import curso_image_names, curso_topics, curso_title

            for name, topics, img_name in zip(curso_title, curso_topics, curso_image_names):
                embed = discord.Embed(title=name, description=topics)
                if(img_name != None):
                    img_path = "imgs/" + str(img_name)
                    file = discord.File(img_path)
                    await message.channel.send(embed=embed, file=file)
                else:
                    await message.channel.send(embed=embed)
    
        if message.content.lower() == "%send graduacao" and message.channel.name == "graduação" and message.author.name == "Franreno":
            from grauacao import graduacao_title, graduacao_topics, link_grade_curricular

            for name, topics in zip(graduacao_title, graduacao_topics):
                if (name != "Graduação - Grade Curricular"):
                    embed = discord.Embed(title=name, description=topics)
                    await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title=name, description=topics)
                    embed.add_field(name="JupiterWeb" , value=link_grade_curricular)
                    await message.channel.send(embed=embed)


        if message.content.lower() == "%send nusp" and message.channel.name == "numero-usp" and message.author.name == "Franreno":
            from nusp import nusp_image_name, nusp_topics, nusp_title

            for name, topics, img_name in zip(nusp_title, nusp_topics, nusp_image_name):
                embed = discord.Embed(title=name, description=topics)
                if(img_name != None):
                    img_path = "imgs/" + str(img_name)
                    file = discord.File(img_path)
                    await message.channel.send(embed=embed, file=file)
                else:
                    await message.channel.send(embed=embed)


        if message.content.lower() == "%send po" and message.channel.name == "perry-oliveira" and message.author.name == "Franreno":
            from perry_oliveira import po_image_name, po_topics, po_title

            for name, topics, img_name in zip(po_title, po_topics, po_image_name):
                embed = discord.Embed(title=name, description=topics)
                if(img_name != None):
                    img_path = "imgs/" + str(img_name)
                    file = discord.File(img_path)
                    await message.channel.send(embed=embed, file=file)
                else:
                    await message.channel.send(embed=embed)

        # if message.content.lower() == "%tocaperry":
        #     voice_channel = message.author.voice
        #     channel = None
        #     if voice_channel != None:
        #         channel = voice_channel.channel.name
        #         vc = await voice_channel.channel.connect()
        #         vc.play(discord.FFmpegPCMAudio('sounds/perrysound.mp3'))
        #         while vc.is_playing():
        #             time.sleep(5)
        #         await vc.disconnect()
        #     else:
        #         response = str(message.author.name) + " não está em um canal de voz."
        #         await message.channel.send(response)
            

client = MyClient()

client.run(TOKEN)
