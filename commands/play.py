import random

import interactions
from interactions import Extension, slash_command, SlashContext, SlashCommandChoice
from interactions.api.events import Component
from tinydb import TinyDB

from automations.log import log_command
from games import tod
from shared import ROOT_DIR, User


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
        game_settings = db.table('game_settings')

        if not game_settings.all():
            await tod.play(ctx, rating, game)
        else:
            host = game_settings.all()[0]['host-id']
            await ctx.send(f"The last game is still ongoing. Ask <@{host}> to stop it first.", ephemeral=True)
        db.close()

    @play.subcommand(
        sub_cmd_name="stop",
        sub_cmd_description="Stop the current game as host",
    )
    async def stop(self, ctx: SlashContext):
        log_command(ctx=ctx, cmd="play.stop")
        db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
        game_settings = db.table('game_settings')

        if game_settings.all():
            if game_settings.search(User['host-id'] == f'{ctx.author.id}'):
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
        game_players = db.table('game_players')

        players = game_players.all()
        if not players:
            await ctx.send("No players found!", ephemeral=True)
        else:
            embed = interactions.Embed(title="Players in current game:", color="#9b59b6")
            for player in players:
                embed.add_field(name=f"- {player['user']}", value=" ", inline=False)
            await ctx.send(embed=embed)
        db.close()

    @interactions.listen(Component)
    async def on_component(self, event: Component):
        btx = event.ctx
        db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
        game_settings = db.table('game_settings')

        if not game_settings.all():
            await btx.send("No game is currently running!", ephemeral=True)
        else:
            game_id = game_settings.get(doc_id=1)['game-id']
            game = game_settings.get(doc_id=1)['game']
            btn_pressed = btx.custom_id.split('.')[1] if btx.custom_id.split('.')[0] == 'tod' else None
            match btn_pressed:
                case "join":
                    if not game_settings.get(User['game-started'] == 'True'):
                        await tod.join(btx)
                    else:
                        await btx.send("The game has already started!", ephemeral=True)
                case "leave":
                    await tod.leave(btx)
                case "start":
                    if game_settings.all():
                        if not game_settings.get(User['game-started'] == 'True'):
                            await tod.start(btx)
                        else:
                            await btx.send("The game has already started!", ephemeral=True)
                    else:
                        await btx.send("No game is currently running!", ephemeral=True)
                case "stop":
                    if game_settings.all():
                        if game_settings.search(User['host-id'] == f'{btx.author.id}'):
                            await tod.stop(btx)
                        else:
                            await btx.send("You're not the host of this game!", ephemeral=True)
                    else:
                        await btx.send("No game is currently running!", ephemeral=True)
                case "continue":
                    await tod.get(btx, 'continue')
                case "skip":
                    await tod.get(btx, 'skip')
                case _:
                    if (btn_pressed.replace('truth', 'tod').replace('dare', 'tod').replace('random', 'tod')) == game_id:
                        match btn_pressed:
                            case "random":
                                await tod.get(btx, (random.choice(['truth', 'dare'])))
                            case _:
                                await tod.get(btx, btn_pressed)
                    else:
                        await btx.send(f"This button is not available in {game}!", ephemeral=True)
        db.close()
