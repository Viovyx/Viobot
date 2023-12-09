from dotenv import load_dotenv
from schedules import schedules
import asyncio
import interactions
from interactions import slash_command, SlashContext
from datetime import datetime
from tinydb import TinyDB, Query
import os
from dateutil.relativedelta import relativedelta
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
User = Query()


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('TEST_TOKEN')
    bot = interactions.Client()

    async def main():
        asyncio.create_task(schedules(bot))
        await bot.astart(token)

    @interactions.listen()
    async def on_startup():
        print("Bot is ready!")

    # logging commands
    def log_command(ctx, cmd):
        db = TinyDB(f'{ROOT_DIR}/db/logs.json', indent=4, create_dirs=True)
        db.default_table_name = f'{cmd}'
        db.insert({
            'time-utc': f'{datetime.utcnow()}',
            'user': f'{ctx.user.username}',
            'user-id': f'{ctx.user.id}',
            'guild-id': f'{ctx.guild_id}',
            'channel': f'{ctx.channel.name}',
            'channel-id': f'{ctx.channel_id}'
        })
        db.close()
        print(f"{ctx.user.username}(uid:{ctx.user.id}) used /{cmd} in {ctx.channel.name}(chid:{ctx.channel_id})(gid:{ctx.guild_id}) at UTC:{datetime.utcnow()}")

    # slash commands
    @slash_command(
        name="ping",
        description="Test bot latency",
        dm_permission=False
    )
    async def ping(ctx: SlashContext):
        log_command(ctx=ctx, cmd="ping")
        await ctx.send(f"Pong! The response time is {bot.latency * 1000}ms")


    @slash_command(
        name="quote",
        description="Quote someone's dumb words",
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name="text",
                description="What do you wish to quote?",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.SlashCommandOption(
                name="user",
                description="Select user to mention",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def quote(ctx: SlashContext, text: str, user: interactions.Member):
        log_command(ctx=ctx, cmd="quote")
        await ctx.send(f'"{text}"\t~{user.mention}')


    @slash_command(
        name="bday-set",
        description="Add your birthday to the bot",
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name="date",
                description="YYYY-MM-DD Example: 1992-01-31 or 2005-12-05",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def bday_set(ctx: SlashContext, date: str):
        log_command(ctx=ctx, cmd="bday-set")
        try:
            adate = date.split("-")
            if len(adate) == 3:
                fdate = datetime(year=int(adate[0]), month=int(adate[1]), day=int(adate[2]))
                if fdate > datetime.now():
                    await ctx.send(f"ERROR: Date can't be in the future", ephemeral=True)
                else:
                    db = TinyDB(f'{ROOT_DIR}/db/bdays.json', indent=4, create_dirs=True)
                    db.default_table_name = 'bdays'
                    if db.search(User['user-id'] == f'{ctx.user.id}'):
                        db.update({'bday': f'{fdate}', 'last-change-utc': f'{datetime.utcnow()}'},
                                  User['user-id'] == f'{ctx.user.id}')
                        await ctx.send(
                            f'Bday succesfully changed for {ctx.user.mention} to {fdate.strftime("%B %d, %Y")}')
                    else:
                        db.insert({
                            'user': f'{ctx.user}',
                            'user-id': f'{ctx.user.id}',
                            'bday': f'{fdate}',
                            'last-change-utc': f'{datetime.utcnow()}'
                        })
                        await ctx.send(f'Bday succesfully set for {ctx.user.mention} to {fdate.strftime("%B %d, %Y")}')
                    db.close()
            else:
                await ctx.send(f"ERROR: Make sure to use the correct seperator '-' and give the year, month and day",
                               ephemeral=True)
        except ValueError:
            await ctx.send(f"ERROR: Date is invalid", ephemeral=True)


    @slash_command(
        name="bday-show",
        description="Show someones bday",
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name="user",
                description="Who's bday do you wish to show?",
                type=interactions.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def bday_show(ctx: SlashContext, user: interactions.Member):
        log_command(ctx=ctx, cmd="bday-show")
        try:
            db = TinyDB(f'{ROOT_DIR}/db/bdays.json', indent=4, create_dirs=True)
            db.default_table_name = 'bdays'
            abday = db.search(User.user == user.username)
            db.close()
            if abday:
                bday_str = abday[0]['bday']
                bday = datetime.strptime(bday_str, '%Y-%m-%d %H:%M:%S')
                age = (datetime.now() - relativedelta(years=int(bday.strftime('%Y')))).strftime('%Y').replace('0', '')

                await ctx.send(f"Bday of {user} is {bday.strftime('%B %d, %Y')} ({age} years old)", ephemeral=True)
            else:
                await ctx.send(f"ERROR: No birthday found for {user}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"ERROR: Something went wrong", ephemeral=True)
            print(e)

    asyncio.run(main())
