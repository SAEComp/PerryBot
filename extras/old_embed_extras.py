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