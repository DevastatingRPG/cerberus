import asyncio, json, discord
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

            reaction, user = await self.bot.wait_for('reaction_add', timeout=120, check=bot_check)
      
            res_movie = search[msg.index(reaction.message)]
            movie_id = res_movie.id
            trailer = discord.utils.get(movies.videos(movie_id), type='Trailer')
            reviews = [review for review in movies.reviews(movie_id) if len(review.content) < 1024]
            similar = '\n'.join([mov.title for mov in movies.similar(movie_id)[0:5]])
            movie_embed = discord.Embed(title='***The Movie Database Search Result***', colour=0xde4035)
            movie_embed.add_field(name='**Title :**', value=res_movie.title)
            movie_embed.add_field(name='\u200b', value='\u200b')
            movie_embed.add_field(name='**Release Date :**', value=res_movie.release_date)
            movie_embed.add_field(name='**Overview :**', value=res_movie.overview, inline=False)
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

            reaction, user = await self.bot.wait_for('reaction_add', timeout=86400, check=bot_check)
            
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

def setup(bot):
    bot.add_cog(Fun(bot))
