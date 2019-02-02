"""
banderplug.py
Author: Jacob Ruzi
This script is intended to be run with an ini formatted configuration file that defines a
'Choose Your Own Adventure' game. See example_game.conf for guidelines on how to format your
game. See BanderPlug.log in the current directory for error details.
"""

import configparser
import logging
import re
import argparse

# Temporary logging settings (eventually will move this to a logging.conf file)
logger = logging.getLogger('banderplug')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('BanderPlug.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class BanderGame:
    """
    BanderGame
    An object holding all configuration details of the game and the user's current place.

    Parameters:
    gameFile - an ini formatted configuration file that defines the game
    saveFile - an ini formatted configuration file that tracks user's progress (not currently supported)
    """

    def __init__(self,gameFile,saveFile=None):
        self.saveFile = None
        self.stage = '0'
        self.title = ''
        # Use helper method to check gameFile validity
        self.__loadStages(gameFile)
        if saveFile:
            self.saveFile = saveFile

    def __failConfiguration(self,message):
        """
        Let the user know the game configuration has failed.
        :param message: A description of the configuration error
        """
        logger.error('Configuration for the game: %s: is incorrect - %s' % (self.title,message))
        exit(1)


    def __loadStages(self,gameFile):
        """
        __loadStages
        This helper method is used by the constructor to check that the gameFile is correctly formatted.
        :param gameFile: an ini formatted configuration file that defines the game
        """
        openGameFile = configparser.ConfigParser()
        openGameFile.read(gameFile)
        stanzas = openGameFile.sections()
        gameStages = {}
        idLinks = []

        # Check for default stanza
        if 'default' not in stanzas:
            self.__failConfiguration('A default stanza is required')

        # Check for default's ID and title
        defaultID = openGameFile['default'].get('id','BAD')
        defaultTitle = openGameFile['default'].get('title','BAD')
        if defaultID!='-1' or defaultTitle=='BAD':
            self.__failConfiguration('The default stanza must have an ID of -1 and a title.')
        self.title = defaultTitle
        logger.info('The game is being configured: %s' % defaultTitle)

        for stanza in stanzas:

            # Check for Valid ID
            stageID = openGameFile[stanza].get('id','BAD')
            try:
                stageID = int(stageID)
            except ValueError as e:
                self.__failConfiguration('The stage - %s - is incorrectly configured: bad id' % stanza)

            # Validate that a previous stage has not already used this ID
            if str(stageID) in gameStages:
                self.__failConfiguration('At least two stages have the same ID: %s' % stageID)

            # Begin creating stage dictionary
            gameStages[str(stageID)] = {}
            stage = gameStages[str(stageID)]

            for key,value in openGameFile[stanza].items():
                if key != 'id':
                    stage[key] = value

            # Fill in default values for potentially empty keys
            if 'gamewinning' not in stage:
                stage['gamewinning'] = 'False'
            if 'gameending' not in stage:
                stage['gameending'] = 'False'

            # Validate stage has a message
            if 'message' not in stage.keys() and stanza!='default':
                self.__failConfiguration('The stage - %s - is incorrectly configured: missing message' % stanza)

            # Validate stage has choices, unless it is the end of the game
            if stage['gameending'] == 'False' and stage['gamewinning'] == 'False' and stanza!='default':
                numChoices = 0
                choicePattern = re.compile(r"choice\.(\d+)")
                for key in stage.keys():
                    matching = choicePattern.match(key)
                    if matching:
                        numChoices += 1
                        if 'response.%s' % matching.group(1) not in stage.keys():
                            self.__failConfiguration('The stage - %s - is missing a response for choice %s' \
                                          % (stanza,matching.group(1)))
                        # Add the response to a list for later verification that the new stage ID exists
                        idLinks.append((stanza,stage['response.%s' % matching.group(1)]))
                if numChoices == 0:
                    self.__failConfiguration('The stage - %s - does not have any choices' % stanza)

        # Validate that choice responses contain valid stage IDs
        for stanza,link in idLinks:
            if link not in gameStages:
                self.__failConfiguration('The stage - %s - links to a nonexistant stage ID: %s' % (stanza,link))

        self.stages = gameStages

    def __presentStage(self, gameOver=False):
        """
        __presentStage
        This helper method is used by the playGame function to present the user's options and check the
        validity of their choices.
        :param gameOver: A boolean representing whether or not the game has ended
        """

        # Get the configuration details for the current game stage
        stageSettings = self.stages[self.stage]

        # Print the stage's message and choices to the console
        print('\n%s' % stageSettings['message'])
        choices = {}
        for key in stageSettings:
            settingName = key.split('.')
            if settingName[0] == 'choice':
                choices[settingName[1]] = stageSettings[key]

        for num,option in sorted(choices.items()):
            print('%s: %s' % (num, option))

        # If the game is not over, the user must make a choice
        if not gameOver:
            waitingForGoodInput = True
            while waitingForGoodInput:
                userChoice = input('Enter the number of your selection: ')
                if 'response.%s' % userChoice in stageSettings:
                    self.stage = stageSettings['response.%s' % userChoice]
                    waitingForGoodInput = False
                else:
                    print('That is not a valid option.')
                    logger.warning('The user did not select a valid choice in stage %s:%s' % (self.stage, userChoice))
            logger.info('The user has moved to stage %s' % self.stage)

    def playGame(self):
        """
        playGame
        The flow of the game is controlled here. The game proceeds until it is ended by a winning or
        losing choice by the user.
        """

        stageSettings = self.stages[self.stage]

        # Keep presenting game stages until the game is over
        while not (stageSettings['gamewinning'] == 'True' or stageSettings['gameending'] == 'True'):
            self.__presentStage()
            stageSettings = self.stages[self.stage]
        self.__presentStage(True)
        if stageSettings['gamewinning'] == 'True':
            print('You won!')
            logger.info('The user won the game')
        elif stageSettings['gameending'] == 'True':
            print('You lost!')
            logger.info('The user lost the game')

    def __str__(self):
        return str(self.stages)

def getArguments():
    """
    Gets the name of the gameFile (and possible saveFile).
    :return: The arguments provided by the user
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('gameFile', help='The ini formatted file with the game configuration')
    parser.add_argument('--saveFile', help='A file to save your game progress')

    return parser.parse_args()

def main():

    args = getArguments()
    myGame = BanderGame(args.gameFile)
    myGame.playGame()

if __name__=="__main__":
    main()