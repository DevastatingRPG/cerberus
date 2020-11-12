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
async def helpfunc(ctx, function='All'):
    channel = ctx.channel
    author = ctx.author
    help_embed = discord.Embed(title='Help', colour=0xde4035)

    help_description = {'init': 'The server owner should use this command to initialize the bot with the Owner, Mod and'
                                ' Co Mod roles\n'
                                'Syntax : .init [Owner role name in quotes] [Mod role name in quotes] [Co Mod role name'
                                ' in quotes]',

                        'info': 'Use this command to get info about all the Moderation roles in the Guild\n'
                                'Syntax : .info',

                        'owner': 'The server owner can use this command to re specify the Owner role\n'
                                 'Syntax : .owner [Owner role in quotes]',

                        'mod': 'The server owner can use this command to re specify the Moderator role\n'
                               'Syntax : .mod [Moderator role in quotes]',

                        'comod': 'The server owner can use this command to re specify the Co Moderator role\n'
                                 'Syntax : .comod [Co Moderator role in quotes]',

                        'kick': 'This command kicks the mentioned user from the server\n'
                                'Syntax: .kick [Mention the user to be kicked here]',

                        'ban': 'This command bans the mentioned user from the server\n'
                               'Syntax: .ban [Mention the user to be banned here]',

                        'unban': 'This command unbans the specified user from the server\n'
                                 'Syntax: .unban [Username of member] [Discord Discriminator of member]',

                        'cr': 'Use this command to create a role in the guild\n'
                              'Syntax : .cr [Name of role to be created]',

                        'dr': 'Use this command to delete a role in the guild\n'
                              'Syntax : .dr [Name of the role to be deleted]',

                        'react': 'Use this command to give roles to users if they react with the green check mark\n'
                                 'Syntax : .react [Name of the role to be given]',

                        'poll': 'Use this command to create a poll\n'
                                'Syntax : .poll [Question in quotes][All the options for the poll in quotes and '
                                'separated by " "]',

                        'help': 'Displays this message\n'
                                'Syntax : .help'}

    if function == 'All':
        for item in help_description.keys():
            help_embed.add_field(name=item, value=help_description[item], inline=False)
        dm_channel = await author.create_dm()
        await dm_channel.send(embed=help_embed)
        await channel.send(f'Hey {author.mention}, I\'ve PMd you a list of my commands!')
    else:
        help_embed.add_field(name=function, value=help_description[function], inline=False)
        await channel.send(embed=help_embed)


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
