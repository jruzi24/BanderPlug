import configparser
import logging
import re

# Temporary logging settings (eventually will move this to a logging.conf file)
logger = logging.getLogger('banderplug')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('BanderPlug.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class BanderGame:

    def __init__(self,gameFile,saveFile=None):
        self.saveFile = None
        self.stage = '0'
        self.__loadStages(gameFile)
        if saveFile:
            self.saveFile = saveFile

    def __loadStages(self,gameFile):
        openGameFile = configparser.ConfigParser()
        openGameFile.read(gameFile)
        stanzas = openGameFile.sections()
        gameStages = {}
        idLinks = []

        for stanza in stanzas:

            # Check for Valid ID
            stageID = openGameFile[stanza].get('id','BAD')
            try:
                stageID = int(stageID)
            except ValueError, e:
                logger.error('The stage - %s - is incorrectly configured: bad id' % stanza)
                exit(1)

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
                logger.error('The stage - %s - is incorrectly configured: missing message' % stanza)
                exit(1)

            # Validate stage has choices, unless it is the end of the game
            if stage['gameending'] == 'False' and stage['gamewinning'] == 'False' and stanza!='default':
                numChoices = 0
                choicePattern = re.compile(r"choice\.(\d+)")
                for key in stage.keys():
                    matching = choicePattern.match(key)
                    if matching:
                        numChoices += 1
                        if 'response.%s' % matching.group(1) not in stage.keys():
                            logger.error('The stage - %s - is missing a response for choice %s' \
                                          % (stanza,matching.group(1)))
                            exit(1)
                        # Add the response to a list for later verification that the new stage ID exists
                        idLinks.append((stanza,stage['response.%s' % matching.group(1)]))
                if numChoices == 0:
                    logger.error('The stage - %s - does not have any choices' % stanza)
                    exit(1)

        # Validate that choice responses contain valid stage IDs
        for stanza,link in idLinks:
            if link not in gameStages:
                logger.error('The stage - %s - links to a nonexistant stage ID: %s' % (stanza,link))
                exit(1)

        self.stages = gameStages

    def __presentStage(self, gameOver=False):
        stageSettings = self.stages[self.stage]

        print('\n%s' % stageSettings['message'])
        choices = {}
        for key in stageSettings:
            settingName = key.split('.')
            if settingName[0] == 'choice':
                choices[settingName[1]] = stageSettings[key]

        for num,option in sorted(choices.items()):
            print('%s: %s' % (num, option))

        if not gameOver:
            waitingForGoodInput = True
            while waitingForGoodInput:
                userChoice = input('Enter the number of your selection: ')
                if 'response.%s' % userChoice in stageSettings:
                    self.stage = stageSettings['response.%s' % userChoice]
                    waitingForGoodInput = False
                else:
                    print('That is not a valid option.')
                    logging.warning('The user did not select a valid choice: %s' % userChoice)

    def playGame(self):
        stageSettings = self.stages[self.stage]
        while not (stageSettings['gamewinning'] == 'True' or stageSettings['gameending'] == 'True'):
            self.__presentStage()
            stageSettings = self.stages[self.stage]
        self.__presentStage(True)
        if stageSettings['gamewinning'] == 'True':
            print('You won!')
        elif stageSettings['gameending'] == 'True':
            print('You lost!')

    def __str__(self):
        return str(self.stages)

def main():

    myGameFile = 'testGame.conf'
    myGame = BanderGame(myGameFile)
    myGame.playGame()

if __name__=="__main__":
    main()
