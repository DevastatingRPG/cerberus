import asyncio, json, discord
from discord.ext import commands

with open('info.json') as info_file:
    server_info = json.load(info_file)

# Custom Checks
def check_if_mod(ctx):
    mod = discord.utils.get(ctx.guild.roles, id=server_info[str(ctx.guild.id)]['mod'])
    return mod in ctx.author.roles

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Function to initialize the bot
    @commands.command(name='init')
    @commands.is_owner()
    async def init(self, ctx, owner: discord.Role, mod: discord.Role, co_mod: discord.Role, nick: discord.TextChannel):

        guild = ctx.guild
        muted = discord.utils.get(guild.roles, name='Muted')

        if muted is None:
            perms = discord.Permissions(send_messages=False)
            await guild.create_role(name='Muted', permissions=perms)

        roles = {member.name: [role.id for role in member.roles] for member in guild.members}

        server_info[str(guild.id)] = {'owner': owner.id, 'mod': mod.id, 'co_mod': co_mod.id, 'roles': roles, 'reaction_roles': {}, 'nick': nick.id}

        with open('info.json', 'w') as info_file_input:
            json.dump(server_info, info_file_input, indent=2)

        await ctx.send(f'Successfully initialized in the Guild with :-')
        await ctx.send(f'Owner role : "{owner}"')
        await ctx.send(f'Moderator role : "{mod}"')
        await ctx.send(f'Co Moderator role : "{co_mod}"')


    # Function to display info of Moderation Roles
    @commands.command(name='info')
    async def info(self, ctx):

        guild = ctx.guild
        await ctx.send(f'Owner role : \"{guild.get_role(server_info[str(ctx.guild.id)]["owner"])}\"')
        await ctx.send(f'Moderator role : \"{guild.get_role(server_info[str(ctx.guild.id)]["mod"])}\"')
        await ctx.send(f'Co Moderator role : \"{guild.get_role(server_info[str(ctx.guild.id)]["co_mod"])}\"')

    # Function to change Owner role
    @commands.command(name='owner')
    @commands.is_owner()
    async def owner_change(self, ctx, *, owner: discord.Role):

        server_info[str(ctx.guild.id)]['owner'] = owner.id

        with open('info.json', 'w') as info_file_input:
            json.dump(server_info, info_file_input, indent=2)

        await ctx.send(f'New owner role is \"{owner}\"')

    # Function to change Moderator role
    @commands.command(name='mod')
    @commands.is_owner()
    async def mod_change(self, ctx, *, mod: discord.Role):

        server_info[str(ctx.guild.id)]['mod'] = mod.id

        with open('info.json', 'w') as info_file_input:
            json.dump(server_info, info_file_input, indent=2)

        await ctx.send(f'New Moderator role is {mod}')

    # Function to change Co Moderator role
    @commands.command(name='comod')
    @commands.is_owner()
    async def comod_change(self, ctx, *, co_mod: discord.Role):

        server_info[str(ctx.guild.id)]['co_mod'] = co_mod.id

        with open('info.json', 'w') as info_file_input:
            json.dump(server_info, info_file_input, indent=2)

        await ctx.send(f'New Co-Moderator role is {co_mod}')

    # Function to kick members along with reason
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):

        if not member.bot:
            dm_channel = await member.create_dm()
            await dm_channel.send(f'Ay Bruh, so.... ya got booted off the server {ctx.guild} due to this reason : {reason}')
        await member.kick(reason=reason)
        await ctx.send(f'{member} got booted lmfaoo !!')
        await ctx.send(f'Okay get a load of this, my sources tell me the reason they were kicked is : {reason}')

    # Function to ban members along with reason
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):

        if not member.bot:
            dm_channel = await member.create_dm()
            await dm_channel.send(f'Ay Bruh, so.... ya got booted permanently off the server {ctx.guild} due to this reason : {reason}')
        await member.ban(reason=reason)
        await ctx.send(f'{member} got booted lmfaoo !!')
        await ctx.send(f'Okay get a load of this, my sources tell me the reason they were banned is : {reason}')

    # Function to unban members
    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member, discriminator):

        bans = await ctx.guild.bans()
        member = discord.utils.find(lambda banned: banned.user.name == member and banned.user.discriminator == discriminator, bans).user
        if not member.bot:
            dm_channel = await member.create_dm()
            await dm_channel.send(f'Ay Bruh, so.... ya ain\'t exiled from "{ctx.guild}" anymore !!')
        await ctx.guild.unban(member)
        await ctx.send(f'{member} is no longer exiled from this server! Poggers !!')

    # Function to Mute members
    @commands.command(name='mute')
    @commands.check(check_if_mod)
    async def mute(self, ctx, member: discord.Member, *, reason=None):

        muted = discord.utils.get(ctx.guild.roles, name='Muted')

        if muted not in member.roles:
            roles = [role.id for role in member.roles]
            server_info[str(ctx.guild.id)]['roles'][member.name] = roles

            with open('info.json', 'w') as info_file_input:
                json.dump(server_info, info_file_input, indent=2)

            avatar = member.avatar_url

            await member.edit(roles=[muted])
            muted_embed = discord.Embed(title='Member Muted', colour=0xde4035)
            muted_embed.set_author(name=member.name, icon_url=avatar)
            muted_embed.add_field(name='Username : ', value=member)
            muted_embed.add_field(name='\u200b', value='\u200b')
            muted_embed.add_field(name='Reason :', value=reason)
            muted_embed.add_field(name='Moderator :', value=ctx.message.author)
            await ctx.send(embed=muted_embed)

        else:
            await ctx.send("He already muted Boah!!")

    # Function to Un-Mute Members
    @commands.command(name='unmute')
    @commands.check(check_if_mod)
    async def unmute(self, ctx, member: discord.Member):

        muted = discord.utils.get(ctx.guild.roles, name='Muted')

        if muted in member.roles:
            roles = server_info[str(ctx.guild.id)]['roles'][member.name]
            roles_list = [ctx.guild.get_role(role) for role in roles]

            avatar = member.avatar_url

            await member.edit(roles=roles_list)
            unmuted_embed = discord.Embed(title='Member Unmuted', colour=0xde4035)
            unmuted_embed.set_author(name=member.name, icon_url=avatar)
            unmuted_embed.add_field(name='Username : ', value=member)
            unmuted_embed.add_field(name='\u200b', value='\u200b')
            unmuted_embed.add_field(name='Moderator :', value=ctx.message.author)
            await ctx.send(embed=unmuted_embed)

        else:
            await ctx.send("He already has the right to speak lmao.")

    # Function to Temp Mute Members 
    @commands.command(aliases= ['tm'])
    @commands.check(check_if_mod)
    async def tempmute(self, ctx, member: discord.Member, duration: int, *, reason=None):

        muted = discord.utils.get(ctx.guild.roles, name='Muted') 

        if muted not in member.roles:

            roles = [role.id for role in member.roles]
            avatar = member.avatar_url

            await member.edit(roles=[muted])
            muted_embed = discord.Embed(title='Member Temp Muted', colour=0xde4035)
            muted_embed.set_author(name=member.name, icon_url=avatar)
            muted_embed.add_field(name='Username : ', value=member)
            muted_embed.add_field(name='\u200b', value='\u200b')
            muted_embed.add_field(name='Reason :', value=reason)
            muted_embed.add_field(name='Moderator :', value=ctx.message.author)
            muted_embed.add_field(name='\u200b', value='\u200b')
            muted_embed.add_field(name='Duration :', value=duration)
            await ctx.send(embed=muted_embed)

            await asyncio.sleep(duration)

            roles = [ctx.guild.get_role(role) for role in roles]
            avatar = member.avatar_url

            await member.edit(roles=roles)
            unmuted_embed = discord.Embed(title='Member Unmuted', colour=0xde4035)
            unmuted_embed.set_author(name=member.name, icon_url=avatar)
            unmuted_embed.add_field(name='Username : ', value=member)
            unmuted_embed.add_field(name='\u200b', value='\u200b')
            unmuted_embed.add_field(name='Moderator :', value=ctx.message.author)
            await ctx.send(embed=unmuted_embed)


        else:
            await ctx.send("He already muted Boah!!")
        
    # Function to clear chat
    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int=1):
        await ctx.channel.purge(limit=amount+1)

    # Function for Reaction Roles
    @commands.command(name='react')
    @commands.has_permissions(manage_roles=True)
    async def react(self, ctx, *, role):

        author = ctx.author
        top_role = author.top_role
        guild = ctx.guild
        channel = ctx.channel

        if top_role.position > discord.utils.get(guild.roles, name=role).position:

            bot_msg_embed = discord.Embed(title='Reaction Role', description=f'React with ✅ to get {role} Role',
                                        colour=0xde4035)
            bot_msg_embed.set_image(url='https://cms.hostelbookers.com/hbblog/wp-content/uploads/sites/3/2012/02/cat-happy-'
                                        'cat-e1329931204797.jpg')
            sent_embed = await channel.send(embed=bot_msg_embed)
            await sent_embed.add_reaction('✅')

            server_info[str(guild.id)]['reaction_roles'][str(sent_embed.id)] = role

            with open('info.json', 'w') as info_file_input:
                json.dump(server_info, info_file_input, indent=2)

        else:
            await channel.send('Oof, your top role is not high enough to run this mate.')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        guild = self.bot.get_guild(payload.guild_id)
        if not guild.get_member(payload.user_id).bot and str(payload.emoji) == '✅' and str(payload.message_id) in server_info[str(guild.id)]['reaction_roles']:     
    
            member = guild.get_member(payload.user_id)
            if str(payload.emoji) == '✅' and not guild.get_member(payload.user_id).bot:
                required_role = server_info[str(guild.id)]['reaction_roles'][str(payload.message_id)]
                await member.add_roles(discord.utils.get(guild.roles, name = required_role))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):

        guild = self.bot.get_guild(payload.guild_id)
        if not guild.get_member(payload.user_id).bot and str(payload.emoji) == '✅' and str(payload.message_id) in server_info[str(guild.id)]['reaction_roles']:
            member = guild.get_member(payload.user_id)
            if str(payload.emoji) == '✅' and not guild.get_member(payload.user_id).bot:
                required_role = server_info[str(guild.id)]['reaction_roles'][str(payload.message_id)]
                await member.remove_roles(discord.utils.get(guild.roles, name = required_role))

    # Function to apply Nickname Change
    @commands.command(name='nick')
    async def nick(self, ctx, *, nickname):

        channel = ctx.guild.get_channel(server_info[str(ctx.guild.id)]['nick'])
        await ctx.message.delete()
        await ctx.send('Nickname change request submitted!')
        request_msg = await channel.send(f'{ctx.author} wants to change their nickname to {nickname}. React with ✅ to accept and ❌ to reject')
        await request_msg.add_reaction('✅')
        await request_msg.add_reaction('❌')

        def reaction_update(reaction, user):
            return not user.bot

        try:

            reaction, user = await self.bot.wait_for('reaction_add', timeout=86400, check=reaction_update)

            if str(reaction.emoji) == '✅':
                await ctx.author.edit(nick=nickname)
                await request_msg.delete()
                await channel.send('Nickname Change request accepted')
                await ctx.send(f'Hey {ctx.author.mention}, Your nickname change request has been accepted')

            if str(reaction.emoji) == '❌':
                await request_msg.delete()
                await channel.send('Nickname Change request rejected')
                await ctx.send(f'Hey {ctx.author.mention}, Your nickname change request has been rejected')

        except asyncio.TimeoutError:
            ctx.send(f'Hey {ctx.author.mention}, it seems your nickname change request has been ignored')

    # Function to Create Role
    @commands.command(aliases=['cr', 'createrole'])
    @commands.has_permissions(manage_roles=True)
    async def create_role(self, ctx, *, role):

        perms = discord.Permissions(add_reactions=True, stream=True, read_messages=True, view_channel=True, send_messages=True, attach_files=True, 
        read_message_history=True, external_emojis=True, connect=True, speak=True, use_voice_activation=True)
        await ctx.guild.create_role(name=role, permissions=perms)
        await ctx.send(f'Role {role} has been successfully created! Poggers!!')

    # Function to Delete Role
    @commands.command(aliases=['deleterole', 'dr'])
    @commands.has_permissions(manage_roles=True)
    async def delete_role(self, ctx, *, role: discord.Role):

        top_role = ctx.author.top_role
        if top_role.position > role.position:
            await role.delete()
            await ctx.send(f'Role {role} has been successfully deleted! Poggers!!')
        else:
            await ctx.send('Oof, your top role is not high enough to run this mate.')

    # Local Error Handling

    @init.error
    async def init_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You need to enter the names of the roles for Owner, Mod and Co-Mod')

    @delete_role.error
    async def dr_handler(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('You cannot delete a role which doesn\t exist, Dum Dum')

def setup(bot):
    bot.add_cog(Moderation(bot))
