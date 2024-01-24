import interactions
import random
from games import tod
from interactions import Extension, slash_command, SlashContext, SlashCommandChoice
from interactions.api.events import Component
from tinydb import TinyDB
from shared import ROOT_DIR, User

from automations.log import log_command


class Play(Extension):
    @slash_command(
        name="play",
        description="Test bot latency",
        dm_permission=False,
        sub_cmd_name="start",
        sub_cmd_description="Play Truth or Dare or another available game!",
        options=[
            interactions.SlashCommandOption(
                name="rating",
                description="The rating will decide what kind of questions you'll get. Rating R disabled by default.",
                type=interactions.OptionType.STRING,
                required=False,
                choices=[
                    SlashCommandChoice(name="PG", value="pg"),
                    SlashCommandChoice(name="PG-13", value="pg13"),
                    SlashCommandChoice(name="R", value="r"),
                ],
            ),
            interactions.SlashCommandOption(
                name="game",
                description="Choose what game to play. Default is Truth or Dare.",
                type=interactions.OptionType.STRING,
                required=False,
                choices=[
                    SlashCommandChoice(name="Truth or Dare", value="tod"),
                    SlashCommandChoice(name="Never Have I Ever", value="nhie"),
                    SlashCommandChoice(name="Would You Rather", value="wyr"),
                    SlashCommandChoice(name="Paranoia", value="paranoia"),
                ],
            ),
        ],
    )
    async def play(self, ctx: SlashContext, rating: str = "", game: str = "tod"):
        log_command(ctx=ctx, cmd="play.start")
        db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
        db.default_table_name = 'game_settings'
        if len(db.all()) == 0:
            await tod.play(ctx, rating, game)
        else:
            host = db.all()[0]['host-id']
            await ctx.send(f"The last game is still ongoing. Ask <@{host}> to stop it first.", ephemeral=True)
        db.close()

    @play.subcommand(
        sub_cmd_name="stop",
        sub_cmd_description="Stop the current game as host",
    )
    async def stop(self, ctx: SlashContext):
        log_command(ctx=ctx, cmd="play.stop")
        db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
        db.default_table_name = 'game_settings'
        if len(db.all()) != 0:
            if db.search(User['host-id'] == f'{ctx.author.id}'):
                await tod.stop(ctx)
            else:
                await ctx.send("You're not the host of this game!", ephemeral=True)
        else:
            await ctx.send("No game is currently running!", ephemeral=True)
        db.close()

    @play.subcommand(
        sub_cmd_name="players",
        sub_cmd_description="Show all players in the current game",
    )
    async def players(self, ctx: SlashContext):
        log_command(ctx=ctx, cmd="play.players")
        db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
        db.default_table_name = 'game_players'
        if len(db.all()) == 0:
            await ctx.send("No players found!", ephemeral=True)
        else:
            embed = interactions.Embed(title="Players in current game:", color="#9b59b6")
            for player in db.all():
                embed.add_field(name=f"- {player['user']}", value=" ", inline=False)
            await ctx.send(embed=embed)

        db.close()

    @interactions.listen(Component)
    async def on_component(self, event: Component):
        btx = event.ctx
        db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
        db.default_table_name = 'game_settings'

        if db.table('game_settings') is None:
            await btx.send("No game is currently running!", ephemeral=True)
        else:
            match btx.custom_id:
                case "tod.join":
                    if not db.get(User['game-started'] == 'True'):
                        await tod.join(btx)
                    else:
                        await btx.send("The game has already started!", ephemeral=True)
                case "tod.leave":
                    await tod.leave(btx, False)
                case "tod.start":
                    if not db.get(User['game-started'] == 'True'):
                        await tod.start(btx)
                    else:
                        await btx.send("The game has already started!", ephemeral=True)
                case "tod.stop":
                    if len(db.all()) != 0:
                        if db.search(User['host-id'] == f'{btx.author.id}'):
                            await tod.stop(btx)
                        else:
                            await btx.send("You're not the host of this game!", ephemeral=True)
                    else:
                        await btx.send("No game is currently running!", ephemeral=True)

                case "tod.truth":
                    await tod.get(btx, 'truth') if db.get(User['game-id'] == 'tod') else await btx.send("This button is only available in Truth or Dare!", ephemeral=True)
                case "tod.dare":
                    await tod.get(btx, 'dare') if db.get(User['game-id'] == 'tod') else await btx.send("This button is only available in Truth or Dare!", ephemeral=True)
                case "tod.random":
                    await tod.get(btx, f"{random.choice(['truth', 'dare'])}") if db.get(User['game-id'] == 'tod') else await btx.send("This button is only available in Truth or Dare!", ephemeral=True)
                case "tod.nhie":
                    await tod.get(btx, 'nhie') if db.get(User['game-id'] == 'nhie') else await btx.send("This button is only available in Never Have I Ever!", ephemeral=True)
                case "tod.wyr":
                    await tod.get(btx, 'wyr') if db.get(User['game-id'] == 'wyr') else await btx.send("This button is only available in Would You Rather!", ephemeral=True)
                case "tod.paranoia":
                    await tod.get(btx, 'paranoia') if db.get(User['game-id'] == 'paranoia') else await btx.send("This button is only available in Paranoia!", ephemeral=True)
                case "tod.skip":
                    await tod.get(btx, 'skip')
                case "tod.continue":
                    await tod.get(btx, 'continue')
                case "tod.leave_continue":
                    await tod.leave(btx, True)
        db.close()
