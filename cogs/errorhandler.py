import discord, traceback, sys
from discord.ext import commands

class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')
        
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('F in the chat, you failed the vibe check to use this lol.')

        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingRole):
            await ctx.send('Oof, you are not powerful enough to run this command.')
        
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        @commands.command(name='repeat', aliases=['mimic', 'copy'])
        async def do_repeat(self, ctx, *, inp: str):
            await ctx.send(inp)

        @do_repeat.error
        async def do_repeat_handler(self, ctx, error):  # pylint: disable=unused-variable

            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'inp':
                    await ctx.send("You forgot to give me input to repeat!")

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
