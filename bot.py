import interactions
from datetime import datetime


def log_command(ctx, cmd):
    print(f"{ctx.user}(uid:{ctx.user.id}) used /{cmd} in {ctx.channel}(chid:{ctx.channel_id})(gid:{ctx.guild_id}) at UTC:{datetime.utcnow()}")


def run_discord_bot(token):
    bot = interactions.Client(token=token)

    @bot.event
    async def on_ready():
        print('Bot is now running!')

    @bot.command(
        name="quote",
        description="Quote someone's dumb words",
        dm_permission=False,
        options=[
            interactions.Option(
                name="text",
                description="What do you wish to quote?",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="user",
                description="Select user to mention",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def quote(ctx: interactions.CommandContext, text: str, user: interactions.Member):
        log_command(ctx=ctx, cmd="quote")
        await ctx.send(f'"{text}"\t~{user.mention}')

    @bot.command(
        name="bday-set",
        description="Add your birthday to the bot",
        dm_permission=False,
        options=[
            interactions.Option(
                name="date",
                description="YYYY-MM-DD Example: 1992-01-31 or 2005-12-05",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def bday_set(ctx: interactions.CommandContext, date: str):
        log_command(ctx=ctx, cmd="bday-set")
        try:
            adate = date.split("-")
            if len(adate) == 3:
                fdate = datetime(year=int(adate[0]), month=int(adate[1]), day=int(adate[2]))
                if fdate > datetime.now():
                    await ctx.send(f"ERROR: Date can't be in the future!", ephemeral=True)
                else:
                    await ctx.send(f"Date valid! {fdate}", ephemeral=True)
            else:
                await ctx.send(f"ERROR: Make sure you give the year, mont and day!", ephemeral=True)
        except ValueError:
            await ctx.send(f"ERROR: Date is invalid!", ephemeral=True)

    @bot.command(
        name="ping",
        description="Test bot latency",
        dm_permission=False
    )
    async def ping(ctx: interactions.CommandContext):
        log_command(ctx=ctx, cmd="ping")
        await ctx.send(f"Pong! The response time is {bot.latency}ms")

    bot.start()
