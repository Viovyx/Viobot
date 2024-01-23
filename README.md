# Viobot
A Discord bot made with Python mainly used for my private server.

The bot uses TinyDB to create file based databases in readable json format. This makes it easy to manage saved data.

## Current command list:
##### General Commands
- `/ping`
- `/quote`
##### Bday Commands
- `/bday add`
- `/bday show`
- `/bday list`
##### Nickname Commands
- `/nickname add`
- `/nickname show`
- `/nickname list`
##### Pairing Commands
- `/pair add`
- `/pair nickname`
- `/pair partner`
- `/pair remove`
- `/pair list`

## In Discord
![image](https://cloud.viovyx.com/index.php/s/ENtL8rSaKB85B8Y/download/viobot.png)

## How to set up?
Make sure to have python3 installed and install the `requirements.txt` packages.

Create a `.env` file at the root of the project containing the following:
```dotenv
TOKEN='<YOUR BOTS TOKEN>'
BDAY_CHANNEL_ID='<THE CHANNEL-ID FOR BDAY MESSAGES>'
```
Make sure to replace the parameters inside `<...>` with your own parameters!

**Any problems? Feel free to contact me on discord: @viovyx**

## TO-DO
- [x] simplify command usage with sub-commands
- [x] add list command for all db's
- [ ] add automatically updated embeds displaying db contents (bdays, nicknames & pairs)
- [ ] add auto added and removed bday role
- [ ] sort list command embeds (bdays, nicknames & pairs)
- [ ] add truth or dare commands with api
- [ ] ...
