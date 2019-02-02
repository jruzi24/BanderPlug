#Overview
The intention of BanderPlug is to easily allow users to create their own "Choose Your Own Adventure" games. Users will require no Python knowledge and can simply create a text based configuration file to share with others.

##Usage
```CLI
usage: banderplug.py [-h] [--saveFile SAVEFILE] gameFile
```

#Configuration
The game configuration file must be created in an .ini format.

##Required Default Stanza
The .ini file must contain a default stanza with an id of -1 and a title, as such:

```ini
[default]
id=-1
title=A Day in the Office
```

##Game Stages
All other stanzas are considered stages of the game. The first game stage must have an id of 0.

All game stages require a message, which describes the stage to the user.

All stages that do not mark the end of the game must have at least one option (and corresponding response). The response is set to the ID of the game stage that is entered as a result of the user's choice.
```ini
[morning]
id=0
message=You wake to the sound of your alarm clock. You better get going to work.
choice.1=Get out of bed.
response.1=1
choice.2=Hit the snooze button.
response.2=2
```

You must define a stage with an ID for each of your available responses.
```ini
[commute]
id=1
message=You're stuck in traffic on your way to work.
choice.1=Take the carpool lane.
response.1=3
choice.2=Honk!
response.2=4
```

If the stage is intended to be an ending to the game, it must have a gameWinning or gameEnding setting set to True. Use gameWinning if the user has won the game, and gameEnding if the user has lost. These stages should not have any user options, since the game is over.
```ini
[snoozed]
id=2
message=You overslept and missed work!
gameEnding=True
```