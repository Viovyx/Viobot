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
    })

    db.default_table_name = 'game_players'
    if db.table('game_players') is not None:
        db.drop_table('game_players')
    db.insert({
        'user': f'{ctx.author.username.removeprefix("@")}',
        'user-id': f'{ctx.author.id}',
    })
    db.default_table_name = 'game_stats'
    if db.table('game_stats') is not None:
        db.drop_table('game_stats')
    db.insert({
        'user': f'{ctx.author.username.removeprefix("@")}',
        'user-id': f'{ctx.author.id}',
        'truth': 0,
        'dare': 0,
        'nhie': 0,
        'wyr': 0,
        'paranoia': 0,
        'skip': 0,
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
        db.default_table_name = 'game_stats'
        db.insert({
            'user': f'{ctx.author.username.removeprefix("@")}',
            'user-id': f'{ctx.author.id}',
            'truth': 0,
            'dare': 0,
            'nhie': 0,
            'wyr': 0,
            'paranoia': 0,
            'skip': 0,
        })
        await ctx.send(f"{ctx.author.mention} joined the game!")
    db.close()


async def leave(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_players'
    if db.search(User['user-id'] == f'{ctx.author.id}'):
        db.remove(User['user-id'] == f'{ctx.author.id}')
        await ctx.send(f"{ctx.author.mention} left the game!")
    else:
        await ctx.send("You're not in the game!", ephemeral=True)
    db.close()


async def start(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_settings'
    db.update({'game-started': 'True'})
    player_id = (random.choice(db.table('game_players').all()))['user-id']
    await ctx.send(f"Next up is <@{player_id}>!")
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
            label="Pass",
            custom_id="tod.pass",
            style=interactions.ButtonStyle.SECONDARY,
        ),
    )
    embed = Embed(
        title="Truth or Dare",
        description=f"It's your turn <@{player_id}>!",
        color="#9b59b6"
    )
    await ctx.send(embed=embed, components=[options], ephemeral=True)
    db.close()


async def stop(ctx):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_settings'
    await ctx.send(
        f"Game '{(db.search(where('game').exists()))[0]['game']}' ended by {ctx.author.mention}!")
    db.drop_table('game_settings')
    db.drop_table('game_players')
    db.drop_table('game_stats')
    db.close()


async def get(ctx, request):
    db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
    db.default_table_name = 'game_settings'
    if db.get(User['game-started'] == 'True'):
        rating = (db.search(where('game').exists()))[0]['rating']
        db.default_table_name = 'game_stats'
        player_id = ctx.author.id

        if request != 'continue':
            db.update({f'{request}': (db.search(User['user-id'] == f'{player_id}'))[0][f'{request}'] + 1},
                      User['user-id'] == f'{player_id}')
        db.close()

        if request != 'skip' and request != 'continue':
            response = (getattr(truthordare, request)(rating))['question']
            embed = Embed(
                title=f"This one is for {ctx.author.username.removeprefix('@')}!",
                description=f"{response}",
                color="#9b59b6",
                fields=[
                    EmbedField(name="Type",
                               value=f"{request.replace('truth', 'Truth').replace('dare', 'Dare').replace('nhie', 'Never Have I Ever').replace('wyr', 'Would You Rather').replace('paranoia', 'Paranoia')}",
                               inline=True),
                    EmbedField(name="Rating", value=f"{rating.upper()}", inline=True),
                ],
            )
            options = ActionRow(
                Button(
                    label="Continue",
                    custom_id="tod.continue",
                    style=interactions.ButtonStyle.PRIMARY,
                ),
                Button(
                    label="Stop",
                    custom_id="tod.stop",
                    style=interactions.ButtonStyle.DANGER,
                ),
            )
            await ctx.send(embed=embed, components=options)
        else:
            db = TinyDB(f'{ROOT_DIR}/db/tod.json', indent=4, create_dirs=True)
            db.default_table_name = 'game_players'
            if len(db.all()) > 1:
                await start(ctx)
            else:
                await ctx.send("There are no more players left in the game! Ending game...")
                await stop(ctx)
            db.close()
    else:
        await ctx.send("There is no game happening currently!", ephemeral=True)
