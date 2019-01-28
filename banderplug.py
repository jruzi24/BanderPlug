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


        for stanza in stanzas:

            # Check for good ID
            stageID = openGameFile[stanza].get('id','-1')
            try:
                stageID = int(stageID)
            except ValueError, e:
                logger.error('The stage - %s - is incorrectly configured: bad id' % stanza)
                exit(1)

            gameStages[str(stageID)] = {}
            stage = gameStages[str(stageID)]

            for key in openGameFile[stanza]:
                if key != 'id':
                    stage[key] = openGameFile[stanza][key]

            if 'message' not in stage.keys() and stanza!='default':
                logger.error('The stage - %s - is incorrectly configured: missing message' % stanza)
                exit(1)
            elif ('gameEnding' not in stage.keys() and 'gameWinning' not in stage.keys()) \
                    or ('gameEnding' not in stage.keys() and openGameFile[stanza]['gameWinning']!='True') \
                    or ('gameWinning' not in stage.keys() and openGameFile[stanza]['gameEnding']!='True'):
                numChoices = 0
                choicePattern = re.compile(r"choice\.(\d+)\s+=")
                for key in stage.keys():
                    matching = choicePattern.match(key)
                    if matching:
                        numChoices += 1
                        if 'response.%s' % matching.group(1) not in stage.keys():
                            logger.error('The stage - %s - is missing a response for choice %s' \
                                          % (stanza,matching.group(1)))
                if numChoices == 0:
                    logger.error('The stage - %s - does not have any choices' % stanza)

        self.stages = gameStages

    def __presentStage(self, gameOver=False):
        stageSettings = self.stages[self.stage]

        print('\n%s' % stageSettings['message'])
        for key in stageSettings:
            settingName = key.split('.')
            if settingName[0] == 'choice':
                print('%s: %s' % (settingName[1], stageSettings[key]))

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
        while not (stageSettings.get('gamewinning',False) or stageSettings.get('gameending',False)):
            self.__presentStage()
            stageSettings = self.stages[self.stage]
        self.__presentStage(True)
        if stageSettings.get('gamewinning', False):
            print('You won!')
        elif stageSettings.get('gameending', False):
            print('You lost!')

    def __str__(self):
        return str(self.stages)

def main():

    myGameFile = 'testGame.conf'
    myGame = BanderGame(myGameFile)
    myGame.playGame()

if __name__=="__main__":
    main()
