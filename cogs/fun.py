import asyncio, json, discord, requests, shutil
from tmdbv3api import TMDb
from tmdbv3api import Movie
from discord.ext import commands

with open('info.json') as info_file:
    server_info = json.load(info_file)

class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        tmdb = TMDb()
        tmdb.api_key = '153134b761348d470176d17a179d0323'
        tmdb.language = 'en'

    # Function to display information about a Movie
    @commands.command(name='movie')
    async def movie(self, ctx, *, title):
        movies = Movie()
        search = movies.search(title)[0:5]  
        searching = await ctx.send('Searching....')
        await asyncio.sleep(3)
        await searching.delete()
        info_msg = await ctx.send(f'{len(search)} results found, React with 👍 on the result you would like to choose.')
        msg = []
        for result in search:
            msg.append(await ctx.send(result))
            await msg[-1].add_reaction('👍')

        try:

            def bot_check(reaction, user):
                return not user.bot and reaction.message in msg and str(reaction.emoji) == '👍'

            reaction, user = await self.bot.wait_for('reaction_add', timeout=120, check=bot_check)  # pylint: disable=unused-variable
      
            res_movie = search[msg.index(reaction.message)]
            movie_id = res_movie.id
            trailer = discord.utils.get(movies.videos(movie_id), type='Trailer')
            reviews = [review for review in movies.reviews(movie_id) if len(review.content) < 1024][0:3]
            similar = '\n'.join([mov.title for mov in movies.similar(movie_id)[0:5]])
            poster = f'https://image.tmdb.org/t/p/w185/{res_movie.poster_path}'
            
            cast = '\n'.join([f"{cast['character']} - {cast['name']}" for cast in movies.credits(movie_id).cast][0:5])  # pylint: disable=no-member
            directors = '\n'.join([director['name'] for director in movies.credits(movie_id).crew if director['job']=='Director'])  # pylint: disable=no-member

            movie_embed = discord.Embed(title='***The Movie Database Search Result***', colour=0xde4035)
            if not poster.endswith('w185/'):
                movie_embed.set_image(url=poster)
            movie_embed.set_author(name='Cerberus', icon_url=str(self.bot.user.avatar_url))
            movie_embed.add_field(name='**Title :**', value=res_movie.title)
            movie_embed.add_field(name='\u200b', value='\u200b')
            movie_embed.add_field(name='**Release Date :**', value=res_movie.release_date)
            movie_embed.add_field(name='**Overview :**', value=res_movie.overview, inline=False)
            movie_embed.add_field(name='**Cast :**', value=cast)
            movie_embed.add_field(name='\u200b', value='\u200b')
            movie_embed.add_field(name='**Directors :**', value=directors)
            if len(reviews) != 0:
                movie_embed.add_field(name='**Reviews :**', value='\u200b')
                for review in reviews:                    
                    movie_embed.add_field(name=f'__{review.author}__', value=review.content, inline=False)
            movie_embed.add_field(name='**Similar Movies :**', value=similar, inline=False)
            await ctx.send(embed=movie_embed)
            await ctx.send(f'~~https://www.youtube.com/watch?v={trailer.key}~~')
            await info_msg.delete()
            for message in msg:
                await message.delete()

        except asyncio.TimeoutError:
            ctx.send('Took too long to respond, cancelling task.')
            for message in msg:
                await message.delete()

    # Function to apply Nickname Change
    @commands.command(name='nick')
    async def nick(self, ctx, *, nickname):

        channel = ctx.guild.get_channel(server_info[str(ctx.guild.id)]['nick'])
        await ctx.message.delete()
        await ctx.send('Nickname change request submitted!')
        request_msg = await channel.send(f'{ctx.author} wants to change their nickname to {nickname}. React with ✅ to accept and ❌ to reject')
        await request_msg.add_reaction('✅')
        await request_msg.add_reaction('❌')

        try:

            def bot_check(reaction, user):
                return not user.bot and reaction.message is request_msg and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

            reaction, user = await self.bot.wait_for('reaction_add', timeout=86400, check=bot_check)  # pylint: disable=unused-variable
            
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

    # Function to create emoji from image link
    @commands.command(name='emoji')
    @commands.has_permissions(manage_emojis=True)
    async def emoji(self, ctx, image: str, *, name: str):
        name = name.replace(' ', '')
        extension = image.split('.')[-1]
        r = requests.get(image, stream=True)        

        if r.status_code == 200:
            
            r.raw.decode_content = True
            
            with open(f'emojis/emoji.{extension}','wb') as image:
                shutil.copyfileobj(r.raw, image)
            
            with open(f'emojis/emoji.{extension}', 'rb') as emoji:
                emoji = emoji.read()
                await ctx.guild.create_custom_emoji(name=name, image=emoji)
                
            ctx.send(f'Emoji succesfully created :{name}:')
        else:
            ctx.send('There was an error retrieving your image')

    @emoji.error
    async def emoji_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send('It seems the emoji limit in the guild has been reached')

def setup(bot):
    bot.add_cog(Fun(bot))
