import interactions
import random
from games import truthordare
from interactions import Extension, slash_command, SlashContext, SlashCommandChoice
from interactions.api.events import Component
from tinydb import TinyDB
from shared import ROOT_DIR, User

from automations.log import log_command


class Tod(Extension):
    @slash_command(
        name="play",
        description="Test bot latency",
        dm_permission=False,
        sub_cmd_name="tod",
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
    async def tod(self, ctx: SlashContext, rating: str = "", game: str = "tod"):
        log_command(ctx=ctx, cmd="play.tod")
        await truthordare.play(ctx, rating, game)


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
                        await truthordare.join(btx)
                    else:
                        await btx.send("The game has already started!", ephemeral=True)
                case "tod.leave":
                    await truthordare.leave(btx)
                case "tod.start":
                    if not db.get(User['game-started'] == 'True'):
                        await truthordare.start(btx)
                    else:
                        await btx.send("The game has already started!", ephemeral=True)
                case "tod.stop":
                    if db.search(User['game-started'] == 'True'):
                        await truthordare.stop(btx)
                    else:
                        await btx.send("The game hasn't started yet!", ephemeral=True)

                case "tod.truth":
                    await truthordare.get(btx, 'truth') if db.get(User['game-id'] == 'tod') else await btx.send("This button is only available in Truth or Dare!", ephemeral=True)
                case "tod.dare":
                    await truthordare.get(btx, 'dare') if db.get(User['game-id'] == 'tod') else await btx.send("This button is only available in Truth or Dare!", ephemeral=True)
                case "tod.random":
                    await truthordare.get(btx, f"{random.choice(['truth', 'dare'])}") if db.get(User['game-id'] == 'tod') else await btx.send("This button is only available in Truth or Dare!", ephemeral=True)
                case "tod.nhie":
                    await truthordare.get(btx, 'nhie') if db.get(User['game-id'] == 'nhie') else await btx.send("This button is only available in Never Have I Ever!", ephemeral=True)
                case "tod.wyr":
                    await truthordare.get(btx, 'wyr') if db.get(User['game-id'] == 'wyr') else await btx.send("This button is only available in Would You Rather!", ephemeral=True)
                case "tod.paranoia":
                    await truthordare.get(btx, 'paranoia') if db.get(User['game-id'] == 'paranoia') else await btx.send("This button is only available in Paranoia!", ephemeral=True)
                case "tod.pass":
                    await truthordare.get(btx, 'skip')
                case "tod.continue":
                    await truthordare.get(btx, 'continue')
        db.close()
