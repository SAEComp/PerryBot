# essential
import os, discord, random
from discord.ext import commands

from database_handler import *


#Special permissions to be able to use the bot
intents = discord.Intents.default()
intents.members = True
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.guilds = True
client = commands.Bot(command_prefix = '%', intents=intents) #bot object


#global random messages variables
lastTwoRandomMessages = ["Gosto mais da Ferb do que Phineas", "SAEComp melhor SA"]

#global roles variables
random_emojis = ["🖐" , "👌" , "🤑" , "🍕" , "🍣" , "🍷" , "🥕" , "✈" , "🎈" , "🎃" , "🖖" , "👋" , "🙏"]
escolher_roles_id = 824803055345336330
# #escolher-jogo channel id == 824803055345336330
# #escolher-ano channel id == 812769812861157410
fora_da_ec_message_id = 827227120035954758

# Request channel variables
requestsChannelDict = {
    "requestChannelOrder": ['016', '017', '018', '019', '020', '021'],
    "categoryID": [832238316387696640, 832238166127149137, 821566511516090428, 821566205239885865, 821566275348070440, 821566366493442108],
    "requestsChannelID": [832238353813471282, 832238243235495986, 832220159598002186, 832220139889098752, 832220124877815848, 832220094050467860],
    "requestsAdminChannelID": 832220500586790943
}

#-------------------------------------------------------------------------------------------
# When the bot logs in
@client.event
async def on_ready():
    print("logged on as ", client.user.name)

    # SearchForTheList.start()

    # Check here the snake game last save in the database ###todo###


@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)

    if channel.id == escolher_roles_id: #roles related
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

    if payload.message_id == fora_da_ec_message_id:
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

    #---------------------------------------------------------Requests related------------------------------------------------------
    if payload.channel_id == requestsChannelDict["requestsAdminChannelID"] and payload.user_id != client.user.id:
        guild = client.get_guild(payload.guild_id)

        # Get the content of the message. Name of channel, where and type
        message = await channel.fetch_message(payload.message_id)
        listEmbeds = message.embeds
        embed = listEmbeds[0]
        description = embed.description.splitlines()
        content = [elem.split(':')[1] for elem in description] #Magick
        content[0] = content[0][1:]
        content[1] = content[1].replace(' ', '')
        content[2] = content[2].replace(' ', '')


        #content should be = ['name', 'where', 'type']
        #get the category of the message
        category = None
        requestChannelID = None
        for categoryName, categoryIDIterator, channelIDIterator in zip(requestsChannelDict["requestChannelOrder"], requestsChannelDict["categoryID"], requestsChannelDict["requestsChannelID"]):
            if str(content[1]) == str(categoryName):
                categoryID = categoryIDIterator
                category = discord.utils.get(guild.categories, id=categoryIDIterator)
                requestChannelID = channelIDIterator

        channelToSendResult = client.get_channel(requestChannelID)

        #check if it was approved of denied
        if str(payload.emoji) == "✅":
            response = "Canal "
            # See if event type is to create channel or delete channel
            if embed.title.lower() == "criar":
                if(content[2] == "text"):
                    await guild.create_text_channel(content[0], category=category)
                elif(content[2] == "voice"):
                    await guild.create_voice_channel(content[0], category=category)
                response = str(content[0]) + " aprovado e criado!"
            
            elif embed.title.lower() == "deletar":
                #content should be = ['name', 'where']
                # Get the text channel with content[0] (name)
                for channel in category.channels:
                    print("To printando aqui; " + str(channel.name)) if "teste" in channel.name else None
                    print("Agora to printando o conteudo[0]: " + str(repr(content[0]))) if "teste" in channel.name else None
                    if str(channel.name).lower() == str(content[0]).lower():
                        print("entrei")
                        await channel.delete()
                        response = str(content[0]) + " deletado!"

            await message.delete(delay=10)
            await channelToSendResult.send(response)
        
        elif(str(payload.emoji) == "❌"):
            await message.delete(delay=10)
            response = "Canal " + str(content[0]) + " rejeitado!"
            await channelToSendResult.send(response)




#-------------------------------------------------------------------------------------------
@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)
    
    #role related
    if channel.id == escolher_roles_id:
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


    if payload.message_id == fora_da_ec_message_id:
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
           
            
#-------------------------------------------------------------------------------------------

@client.command(name="role")    
async def RoleManipulation(ctx, *, args):
    guild = ctx.guild
    
    splitted = args.split(' ')

    if splitted[0] == "add":
        splitted.pop(0)

        if(len(splitted) == 0):
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
            if role_name.lower() == role.name.lower():
                response = "Essa role já existe!"
                await ctx.channel.send(response)
                return

        #Create the role with the name args
        color = random.randint(0,16777215)
        await guild.create_role(name=role_name, colour=color)

        response_at_channel = "Role criada!"
        await ctx.channel.send(response_at_channel)

        channel = client.get_channel(escolher_roles_id)
        embed = discord.Embed(title=str(role_name.upper()), description="Reaja a esta mensagem para ganhar a role")
        message = await channel.send(embed=embed)
        await message.add_reaction(random.choice(random_emojis))


    #-------------------------------------------------------------------------------------------

    #remove role if member is from SaeComp
    elif splitted[0] == "remove":
        splitted.pop(0)

        if(len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)

        flag = False
        for role in ctx.author.roles: 
            if role.name == "SaeComp": flag = True

        if(flag == True):
            for role in guild.roles:
                if role.name.lower() == role_name.lower():
                    channel = client.get_channel(escolher_roles_id)
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

    #-------------------------------------------------------------------------------------------
    #list all the members from a role
    elif splitted[0] == "list":
        splitted.pop(0)
        if(len(splitted) == 0 ):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return
        
        role_name = ' '.join(splitted)
        flag = False
        for role in guild.roles:
            if role_name.lower() == role.name.lower():
                flag = True
                role_id = role.id
        
        if(flag == True):
            #get all role memebers
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
        
    #role help format
    elif splitted[0] == "help":
        response = "Digite %role add [nome]: para adicionar uma role nova\nDigite %role list [role]: para listar todos os membros desta role"
        await ctx.channel.send(response)

    #-------------------------------------------------------------------------------------------

    else:
        response = "Formato errado\nDigite %role help"
        await ctx.channel.send(response)

    
#-------------------------------------------------------------------------------------------

#random messages handling
@client.command(name="random")
async def HandleRandomEvents(ctx, *args):

    largs = list(args)
  
    if(len(largs) == 0):
        #send here the random message

        flag = False
        while flag == False:
            try:
                ret = get_random_text()
            except:
                pass

            if ret != lastTwoRandomMessages[0]: 
                flag = True
                lastTwoRandomMessages[1] = lastTwoRandomMessages[0]
                lastTwoRandomMessages[0] = ret
                break
        
        await ctx.channel.send(ret)
        

    elif(largs[0] == "add"):
        #add the message into the database
        largs.pop(0)
        if(len(largs) == 0):
            await ctx.channel.send("Formato errado digite %random help")
            return
        
        #add data
        new_message = ' '.join(largs)
        
        try:
            add_random_text(new_message)
        except:
            await ctx.channel.send("Essa mensagem já existe")
            return

        response = new_message + " adicionado!"
        await ctx.channel.send(response)


    elif(largs[0] == "remove"):
        largs.pop(0)
        if(len(largs) == 0):
            await ctx.channel.send("Formato errado digite %random help")
            return
        
        message_to_remove = ' '.join(largs)

        try:
            remove_random_text(message_to_remove)
        except:
            await ctx.channel.send("Mensagem inexistente")
            return

        await ctx.channel.send("Mensagem removida")


    elif(largs[0] == "help"):
        response = "    ->%random: para uma mensagem aleatoria\n->%random add [mensagem]: adiciona a mensagem digitada\n->%random remove [mensagem]: remove a mensagem digitada"
        await ctx.channel.send(response)

    #list all the messages ###MUST BE USED WITH CAUTION###
    elif(largs[0] == "list"):
        flag = False
        for role in ctx.author.roles: 
            if role.name == "SaeComp": flag = True
        if(flag == True):
            all_text = get_all_text()
            for text in all_text:
                await ctx.channel.send(text[0])
    else:
        response = "Formato errado\n    ->%random: para uma mensagem aleatoria\n    ->%random add [mensagem]: adiciona a mensagem digitada\n    ->%random remove [mensagem]: remove a mensagem digitada"
        await ctx.channel.send(response)


#------------------------------------------------------------------------------------------------------------------------------------------------------
                                            ### REQUESTS TO CREATE/DELETE ANOTHER CHANNEL ###

@client.command(name="request")
async def HandleRequestsInput(ctx, *, args):
    # Request's input should be %request create/delete <name> <type=text(default)>
    # When the request is made, it will be sent to the admin category waiting for the approval of anyone from SaeComp
    # Reactions types: ✅ ❌
    # The message sent to the admin panel will be an embed and have the <name> of the new channel as a title, 
    # where it was made, 018,019,020,021,etc. And it's <type> text by default or channel if specified
    
    
    # Check if the request was made from one of the requests channels.
    if ctx.channel.id not in requestsChannelDict["requestsChannelID"]:
        await ctx.channel.send("Este comando só pode ser usado em um dos canais de requests.")
        return


    requestInput = args.split(' ')
    wrong_format = "Formato errado! Digite %request help"
    

    if(requestInput[0].lower() == "create"): # Handle creation of channels
        requestInput.pop(0) # Remove Create word
        if (len(requestInput) == 0):
            await ctx.channnel.send(wrong_format)
            return

        # Verify if the last pos has the input type
        lastpos = requestInput[len(requestInput)-1]
        channelType = "text"
        if(lastpos.lower() == "text" or lastpos.lower() == "voice"):
            #if it has check if its voice
            if(lastpos.lower() == "voice"):
                channelType = "voice"
        #then discard the last element of the list
        requestInput.pop()

        if(len(requestInput) == 0):
            await ctx.channel.send(wrong_format)
            return

        channelName =  ' '.join(requestInput)


        # Verify if the name of the requested channel already exists.
        channelTheMessageWasSent = ctx.channel
        categoryOfMessageSent = channelTheMessageWasSent.category
        for channelInCategory in categoryOfMessageSent.channels:
            if channelName.lower() == channelInCategory.name.lower():
                await ctx.channel.send("Ação inválida, canal já existe!")
                return

        # Now send to the requests-admin channel
        title = "Criar"
        description = "Criar canal com nome: " + str(channelName) + "\nEstá sendo criado na categoria: " + str(categoryOfMessageSent) + "\nTipo: " + str(channelType)

        embed = discord.Embed(title=title, description=description)

        requestAdminChannel = client.get_channel(requestsChannelDict["requestsAdminChannelID"])
        messageAdmin = await requestAdminChannel.send(embed=embed)
        await messageAdmin.add_reaction("✅")        
        await messageAdmin.add_reaction("❌")        
        await ctx.channel.send("Pedido feito! Espere ser aprovado por alguem da SAEComp")

        return

    
    elif(requestInput[0].lower() == "delete"): # Handle removal of channels
        requestInput.pop(0) #remove delete word
        if(len(requestInput) == 0):
            await ctx.channnel.send(wrong_format)
            return
    
        # Verify if the last pos has the input type
        lastpos = requestInput[len(requestInput)-1]
        channelType = "text"
        if(lastpos.lower() == "text" or lastpos.lower() == "voice"):
            #if it has check if its voice
            if(lastpos.lower() == "voice"):
                channelType = "voice"
        #then discard the last element of the list
        requestInput.pop()

        if(len(requestInput) == 0):
            await ctx.channel.send(wrong_format)
            return
            
        channelName =  ' '.join(requestInput) if channelType == "voice" else '-'.join(requestInput)

        # Verify if the channel exists
        doesChannelExists = False
        channelTheMessageWasSent = ctx.channel
        categoryOfMessageSent = channelTheMessageWasSent.category
        for channelInCategory in categoryOfMessageSent.channels:
            if channelName.lower() == channelInCategory.name.lower():
                doesChannelExists = True

        if doesChannelExists:
            # Create the message to delete certain channel
            title = "Deletar" 
            description = description = "Deletando canal com nome: " + str(channelName) + "\nEstá sendo deletado na categoria: " + str(categoryOfMessageSent) + "\nTipo: " + str(channelType)
            embed = discord.Embed(title=title, description=description)
            requestAdminChannel = client.get_channel(requestsChannelDict["requestsAdminChannelID"])
            messageAdmin = await requestAdminChannel.send(embed=embed)
            await messageAdmin.add_reaction("✅")        
            await messageAdmin.add_reaction("❌")
            await ctx.channel.send("Pedido feito! Espere ser aprovado por alguem da SAEComp")
        
        else:
            await ctx.channel.send("Esse canal não existe.")
        
        return

    elif(requestInput[0].lower() == "help"):
        helpResponse = "Para pedir um canal de texto ou voz use o comando:\n%request <create/delete> <nome> <tipo>\nO <tipo> pode ser TEXT ou VOICE. Se não for especificado será criado como um canal de texto."
        await ctx.channel.send(helpResponse)
        return
    
#------------------------------------------------------------------------------------------------------------------------------------------------------


@client.event
async def on_message(ctx):
    
    if ctx.author == client.user:
        return

    #greetings
    if ctx.content.lower() == "oi perry":
        if ctx.author.nick == None:
                response = "Oi " + str(ctx.author.name) + '!'
        else:
            response = "Oi " + str(ctx.author.nick) + '!'
        await ctx.channel.send(response)
        
    if ctx.content.lower() == "bcc":
        await ctx.channel.send("#XUPABCC")

    if ctx.content.lower() == "federal":
        await ctx.channel.send("#XUPAFEDERAL")

    await client.process_commands(ctx)

secret_token = None
try:
    secret_token = os.environ["TOKEN"]
except:
    from secret_keys import TOKEN
    secret_token = TOKEN
    
client.run(secret_token)