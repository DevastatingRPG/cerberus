# bot.py
import discord, random, asyncio, youtube_dl, os, json
from discord.ext import commands
from tmdbv3api import TMDb
from tmdbv3api import Movie
from youtubesearchpython import SearchVideos


TOKEN='NzYzNjk3ODI5NjU4NDkyOTM5.X37fBw.lKqVTEJ9skgOJslDUqi0hC0Z2y8'

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

tmdb = TMDb()
tmdb.api_key = '153134b761348d470176d17a179d0323'
tmdb.language = 'en'

with open('info.json') as info_file:
    server_info = json.load(info_file)

# Log in the console when bot is connected
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name='.help'))
    print(f'{bot.user.name} has connected to Discord!')


# Function to Create Poll
@bot.command(name='poll')
async def poll(ctx, question: str, options='Yes No'):

    reactions = {0: '0️⃣', 1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣', 9: '9️⃣'}
    new_options = options.split(' ')
    channel = ctx.channel

    poll_embed = discord.Embed(title='Poll', description=question, colour=0xde4035)

    for option in new_options:
        reaction = reactions[new_options.index(option)]
        poll_embed.add_field(name=reaction, value=option)

    sent_embed = await channel.send(embed=poll_embed)
    for option in new_options:
        await sent_embed.add_reaction(reactions[new_options.index(option)])


# Function to display information about a Movie
@bot.command(name='movie')
async def movie(ctx, *, title):
    guild = ctx.guild
    movies = Movie()
    search = movies.search(title)
    if len(search) >= 5:
        search = search[0:5]    
    results = []
    searching = await ctx.send('Searching....')
    await asyncio.sleep(3)
    await searching.delete()
    info_msg = await ctx.send(f'{len(search)} results found, React with 👍 on the result you would like to choose.')
    for index in range(len(search)):
        results.append(await ctx.send(search[index]))
        await results[index].add_reaction('👍')

    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        member = guild.get_member(payload.user_id)
        message = await ctx.fetch_message(payload.message_id)
        if str(payload.emoji) == '👍' and not member.bot:

            ind = results.index(message)
            res_movie = search[ind]
            movie_id = res_movie.id
            videos = movies.videos(movie_id)
            trailer = discord.utils.get(videos, type='Trailer')
            reviews = movies.reviews(movie_id)
            similar = movies.similar(movie_id)

            if len(similar) >= 5:
                similar = similar[0:5]
            similar_content = ''
            for mov in similar:
                similar_content += f'{mov.title}\n'
            if len(reviews) >= 3:
                reviews = reviews[0:3]

            movie_embed = discord.Embed(title='***The Movie Database Search Result***', colour=0xde4035)
            movie_embed.add_field(name='**Title :**', value=res_movie.title)
            movie_embed.add_field(name='\u200b', value='\u200b')
            movie_embed.add_field(name='**Release Date :**', value=res_movie.release_date)
            movie_embed.add_field(name='**Overview :**', value=res_movie.overview, inline=False)
            movie_embed.add_field(name='**Reviews :**', value='\u200b')
            for review in reviews:
                if len(review.content) < 1024:
                    movie_embed.add_field(name=f'__{review.author}__', value=review.content, inline=False)
            movie_embed.add_field(name='**Similar Movies :**', value=similar_content, inline=False)
            await ctx.send(embed=movie_embed)
            await ctx.send(f'~~https://www.youtube.com/watch?v={trailer.key}~~')
            await info_msg.delete()
            for message in results:
                await message.delete()


# Custom Help
@bot.command(name='help')
async def helpfunc(ctx, category=None):

    help_embed = discord.Embed(title='Cerberus Command List', colour=0xde4035)

    moderation =   {'init':         'Initialize the bot in the server\n'
                                    'Syntax : `.init [Owner role] [Mod role name] [Co-Mod role name] [Text Channel for nicknames]`',

                    'info':         'Get Server Info\n'
                                    'Syntax : `.info`',

                    'owner':        'Change Owner role\n'
                                    'Syntax : `.owner [Owner role]`',

                    'mod':          'Change Mod role\n'
                                    'Syntax : `.mod [Mod role]`',

                    'comod':        'Change Co-Mod role\n'
                                    'Syntax : `.comod [Co-Mod role]`',

                    'kick':         'Kick member from guild\n'
                                    'Syntax : `.kick [User] [Reason]`',

                    'ban':          'Ban member from guild\n'
                                    'Syntax : `.ban [User] [Reason]`',

                    'unban':        'Unban user from guild\n'
                                    'Syntax : `.unban [Username] [Discord Discriminator]`',

                    'mute':         'Mute member\n'
                                    'Syntax : `.mute [User] [Reason]`',

                    'unmute':       'Unmute member\n'
                                    'Syntax : `.unmute [User]`',

                    'tempmute':     'Mute member for specified time\n'
                                    'Syntax : `.mute [User] [Duration(seconds)] [Reason]`',

                    'createrole':   'Create role\n'
                                    'Syntax : `.cr [Role]`',

                    'deleterole':   'Delete role\n'
                                    'Syntax : `.dr [Role]`',

                    'react':        'Create reaction role\n'
                                    'Syntax : `.react [Role]`',
                                    
                    'clear':        'Clear messages\n'
                                    'Syntax : `.clear [No. of msgs]`'}

    fun =  {'nick':     'Change nickname in guild\n'
                        'Syntax : `.nick [Nickname]`',
                        
            'poll':     'Create Poll\n'
                        'Syntax : `.poll [Question in quotes] [Options in quotes separated by spaces]`',
                        
            'movie':    'Show information about a Movie\n'
                        'Syntax : `.movie [Movie name]`'}

    help_embed = {'⚙️ **Moderation**': '`.help moderation`', '\u200b': '\u200b', '😁 **Fun**': '`.help fun`'}
    reference = {'⚙️': [moderation, 'Moderation', ['⬅️'], False], '😁': [fun, 'Fun', ['⬅️'], False], '⬅️': [help_embed, 'Home Page', ['⚙️', '😁'], True]}

    categories = {'moderation': reference['⚙️'], 'fun': reference['😁']}

    def make_embed(info):
        new_embed = discord.Embed(title='Cerberus Command List', colour=0xde4035, description=info[1])
        avatar = str(bot.user.avatar_url)
        new_embed.set_thumbnail(url=avatar)
        for pair in list(info[0].items()):
            new_embed.add_field(name=pair[0], value=pair[1], inline=info[3])
        return new_embed

    
    if category is None:
        sent_embed = await ctx.send(embed=make_embed(reference['⬅️']))
        for category in list(reference.keys()):
            if category != '⬅️':
                await sent_embed.add_reaction(category)
    
    else:
        sent_embed = await ctx.send(embed=make_embed(categories[category]))
        await sent_embed.add_reaction('⬅️')
    
    async def check_reactions(ctx):
        while True:
            reaction, user = await bot.wait_for('reaction_add')
            if reaction.message.id == sent_embed.id and not user.bot:
                await sent_embed.clear_reactions()
                await sent_embed.edit(embed=make_embed(reference[str(reaction.emoji)]))
                for reactions in reference[str(reaction.emoji)][2]:
                    await sent_embed.add_reaction(reactions)

    bot.loop.create_task(check_reactions(ctx))




# Error Handling section
# @bot.event
# async def on_command_error(ctx, error):
#     channel = ctx.channel
#
#     if isinstance(error, commands.CheckFailure):
#         await channel.send('F in the chat, you are not powerful enough to use this lol.')
#
#     if isinstance(error, commands.CommandInvokeError):
#         await channel.send('You hold no power over the Fuhrer, Child.')
#
#     if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingRole):
#         await channel.send('Oof, you are not powerful enough to run this command.')
#

bot.run(TOKEN)  # run the bot as usual
