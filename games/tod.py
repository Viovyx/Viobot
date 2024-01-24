import random

import interactions
from interactions import ActionRow, Button, Embed, EmbedField
from tinydb import TinyDB, where

import truthordare
from shared import ROOT_DIR
from shared import User


async def play(ctx, rating, game):
    join_menu = ActionRow(
        Button(
            label="Join",
            custom_id="tod.join",
            style=interactions.ButtonStyle.SUCCESS,
        ),
        Button(
            label="Leave",
            custom_id="tod.leave",
            style=interactions.ButtonStyle.DANGER,
        ),
    )

    start_menu = ActionRow(
        Button(
            label="Start",
            custom_id="tod.start",
            style=interactions.ButtonStyle.PRIMARY,
        ),
        Button(
            label="Stop",
            custom_id="tod.stop",
            style=interactions.ButtonStyle.DANGER,
        ),
    )

    info_embed = Embed(
        title=f"{game.replace('tod', 'Truth or Dare').replace('nhie', 'Never Have I Ever').replace('wyr', 'Would You Rather').replace('paranoia', 'Paranoia')}",
        description="Waiting for the host to start the game...",
        color="#9b59b6",
        fields=[
            EmbedField(name="Host", value=ctx.author.mention, inline=True),
            EmbedField(name="Rating", value=f"{rating.upper() if rating else 'default'}", inline=True),
        ],
    )

    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_settings'
    if db.table('game_settings') is not None:
        db.drop_table('game_settings')
    db.insert({
        'game': f"{game.replace('tod', 'Truth or Dare').replace('nhie', 'Never Have I Ever').replace('wyr', 'Would You Rather').replace('paranoia', 'Paranoia')}",
        'game-id': f'{game}',
        'rating': f'{rating if rating else "default"}',
        'host': f'{ctx.author.username.removeprefix("@")}',
        'host-id': f'{ctx.author.id}',
        'game-started': 'False',
        'btn_state': 'disabled',
    })

    db.default_table_name = 'game_players'
    if db.table('game_players') is not None:
        db.drop_table('game_players')
    db.insert({
        'user': f'{ctx.author.username.removeprefix("@")}',
        'user-id': f'{ctx.author.id}',
    })
    db.close()

    await ctx.send(embed=info_embed, components=[join_menu])
    await ctx.send(
        "You're hosting this game! Wait for everyone to join and then use these buttons to Start/Stop the game:",
        components=[start_menu], ephemeral=True)


async def join(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_players'

    if db.search(User['user-id'] == f'{ctx.author.id}'):
        await ctx.send("You're is already in the game!", ephemeral=True)
    else:
        db.insert({
            'user': f'{ctx.author.username.removeprefix("@")}',
            'user-id': f'{ctx.author.id}',
        })
        await ctx.send(f"{ctx.author.mention} joined the game!")
    db.close()


async def leave(ctx, continue_game: bool):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_players'
    if db.search(User['user-id'] == f'{ctx.author.id}'):
        db.remove(User['user-id'] == f'{ctx.author.id}')
        await ctx.send(f"{ctx.author.mention} left the game!")
        if len(db.all()) == 0:
            await ctx.send("There are no more players left in the game! Ending game...")
            await stop(ctx)
        elif continue_game is True:
            await get(ctx, 'continue')
    else:
        await ctx.send("You're not in the game!", ephemeral=True)
    db.close()


async def start(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_settings'
    db.update({'game-started': 'True', 'btn_state': 'enabled'})
    game = (db.search(where('game').exists()))[0]['game']
    player_id = (random.choice(db.table('game_players').all()))['user-id']
    options = None
    match (db.search(where('game-id').exists()))[0]['game-id']:
        case "tod":
            options = ActionRow(
                Button(
                    label="Truth",
                    custom_id="tod.truth",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
                Button(
                    label="Dare",
                    custom_id="tod.dare",
                    style=interactions.ButtonStyle.DANGER,
                ),
                Button(
                    label='Random',
                    custom_id='tod.random',
                    style=interactions.ButtonStyle.PRIMARY,
                ),
            )
        case "nhie":
            options = ActionRow(
                Button(
                    label="Play",
                    custom_id="tod.nhie",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
            )
        case "wyr":
            options = ActionRow(
                Button(
                    label="Play",
                    custom_id="tod.wyr",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
            )
        case "paranoia":
            options = ActionRow(
                Button(
                    label="Play",
                    custom_id="tod.paranoia",
                    style=interactions.ButtonStyle.SUCCESS,
                ),
            )
    options.add_component(
        Button(
            label="Skip",
            custom_id="tod.skip",
            style=interactions.ButtonStyle.SECONDARY,
        ),
    )
    embed = Embed(
        title=game,
        description=f"It's your turn <@{player_id}>! Choose an option to continue the game:",
        color="#9b59b6"
    )
    await ctx.send(embed=embed, components=[options])
    db.close()


async def stop(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_settings'
    await ctx.send(
        f"Game '{(db.search(where('game').exists()))[0]['game']}' ended by {ctx.author.mention}!")
    db.drop_table('game_settings')
    db.drop_table('game_players')
    db.close()


async def get(ctx, request):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_settings'
    if db.get(User['game-started'] == 'True'):
        db.default_table_name = 'game_players'
        players = [db.table('game_players').all()[i]['user-id'] for i in range(len(db.table('game_players').all()))]
        db.default_table_name = 'game_settings'
        rating = (db.search(where('game').exists()))[0]['rating']
        player_id = ctx.author.id

        if str(player_id) not in players:
            await ctx.send("You're not in the game!", ephemeral=True)
            return

        if request != 'continue':
            btn_state = (db.search(where('btn_state').exists()))[0]['btn_state']
            if btn_state == 'disabled':
                await ctx.send("The button has already been pressed! Wait for the game to continue.", ephemeral=True)
                return
            db.update({'btn_state': 'disabled'})

        if request == 'skip':
            await ctx.send(f"<@{player_id}> skipped!")

        if request != 'skip' and request != 'continue':
            response = (getattr(truthordare, request)(rating if rating != 'default' else None))['question']
            game = (db.search(where('game').exists()))[0]['game']
            db.close()
            embed = Embed(
                title=f"{game}",
                description=f"{response}",
                color="#9b59b6",
                fields=[
                    EmbedField(name="Type",
                               value=f"{request.replace('truth', 'Truth').replace('dare', 'Dare').replace('nhie', 'Never Have I Ever').replace('wyr', 'Would You Rather').replace('paranoia', 'Paranoia')}",
                               inline=True),
                    EmbedField(name="Rating", value=f"{rating.upper()}", inline=True),
                    EmbedField(name="Initiated by", value=f"<@{player_id}>", inline=True),
                ],
            )
            options = ActionRow(
                Button(
                    label="Continue",
                    custom_id="tod.continue",
                    style=interactions.ButtonStyle.PRIMARY,
                ),
                Button(
                    label="Leave",
                    custom_id="tod.leave_continue",
                    style=interactions.ButtonStyle.DANGER,
                ),
            )
            await ctx.send(embed=embed, components=options)
        else:
            db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
            db.default_table_name = 'game_players'
            if db.all() is not None:
                await start(ctx)
            else:
                await ctx.send("There are no more players left in the game! Ending game...")
                await stop(ctx)
            db.close()
    else:
        await ctx.send("There is no game happening currently!", ephemeral=True)
