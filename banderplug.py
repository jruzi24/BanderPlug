import configparser

class BanderGame:

    def __init__(self,gameFile,saveFile=None):
        self.saveFile = None
        self.stage = '0'
        self.stages = self.__loadStages(gameFile)
        if saveFile:
            self.saveFile = saveFile

    def __loadStages(self,gameFile):
        openGameFile = configparser.ConfigParser()
        openGameFile.read(gameFile)
        stanzas = openGameFile.sections()
        gameStages = {}

        for stanza in stanzas:
            gameStages[openGameFile[stanza]['id']] = {}
            stage = gameStages[openGameFile[stanza]['id']]
            for key in openGameFile[stanza]:
                if key != 'id':
                    stage[key] = openGameFile[stanza][key]

            # Check stanza has required settings
            # Need work here

        return gameStages

    def __presentStage(self):
        stageSettings = self.stages[self.stage]
        print('\n%s' % stageSettings['message'])
        userChoice = input('Enter your selection: ')

        self.stage = stageSettings['response.%s' % userChoice]

    def playGame(self):
        stageSettings = self.stages[self.stage]
        while not (stageSettings.get('gamewinning',False) or stageSettings.get('gameending',False)):
            self.__presentStage()
            stageSettings = self.stages[self.stage]
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
    #print(myGame)

if __name__=="__main__":
    main()