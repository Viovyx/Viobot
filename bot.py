import interactions


def log_command(u, cmd):
    print(f"{u}(id:{u.id}) used /{cmd}")


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
        log_command(ctx.user, "quote")
        await ctx.send(f'"{text}"\t-{user.mention}')

    @bot.command(
        name="bday",
        description="Add your birthday to the bot",
        dm_permission=False,
        options=[
            interactions.Option(
                name="day",
                description="Enter the day of your bday. e.g. 5 or 10",
                type=interactions.OptionType.INTEGER,
                required=True,
            ),
            interactions.Option(
                name="month",
                description="Enter the month of your bday. e.g. 12 or 4",
                type=interactions.OptionType.INTEGER,
                required=True,
            ),
            interactions.Option(
                name="year",
                description="Enter the year of your bday. e.g. 1995 or 2007",
                type=interactions.OptionType.INTEGER,
                required=True,
            ),
        ],
    )
    async def bday(ctx: interactions.CommandContext, day: int, month: int, year: int):
        log_command(ctx.user, "bday")
        # to-do

    @bot.command(
        name="ping",
        description="Test bot latency"
    )
    async def ping(ctx: interactions.CommandContext):
        log_command(ctx.user, "ping")
        await ctx.send(f"Pong! The response time is {bot.latency}ms")

    bot.start()
