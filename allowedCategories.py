import pandas as pd
import json

badWords = pd.read_csv('trainData/badWords.csv')


class AllowedCategories:
    __allowed: set
    __serverId: int
    __settings: dict
    badWordsCategories = set(badWords['category_1'])
    JSONfileName = 'data.json'

    def __init__(self, serverId: int):
        self.__serverId = serverId
        with open(self.JSONfileName, 'r') as f:
            data = json.load(f)
    
        for item in data:
            if item.get('id') == serverId:
                self.__allowed = set(item.get('categories', []))
                self.__settings = item.get('settings')
                return
        else:
            self.__settings = {            
                "filterHate": True,
                "filterScam": True,
                "filterSpam": True,
                "blurHateImages": True
            }
            self.__allowed = set()
            new_entry = {'id': serverId, 'categories': list(self.__allowed), 'settings': self.__settings}
            data.append(new_entry)
            with open(self.JSONfileName, 'w') as f:
                json.dump(data, f, indent=4)

        
        
    def pushCategory(self, newCategory: str) -> bool: # True - success, False - error (category not exists)
        if newCategory not in AllowedCategories.badWordsCategories:
            return False
        
        self.__allowed.add(newCategory)
        self._save_to_json()
        return True
    
    def removeCategory(self, toRemove: str) -> bool: # True - success, False - category not in allowed
        if toRemove not in self.__allowed:
            return False
        
        self.__allowed.remove(toRemove)
        self._save_to_json()
        return True

    def getAllowedCategories(self) -> set:
        return self.__allowed
    
    def filterWords(self, offensiveWords: list) -> set | list:
        res = []
        if len(self.__allowed) == 0:
            return offensiveWords
        
        for word in offensiveWords:
            if word[1] in self.__allowed:
                res.append(word)

        return res
    
    def clear(self):
        self.__allowed.clear()
        self._save_to_json()

    def setSettings(self, newSettings: dict):
        if (type(newSettings) != dict):
            return
        
        self.__settings = newSettings
        self._save_to_json()

    def getSettings(self):
        return self.__settings

    def _save_to_json(self):
        with open(self.JSONfileName, 'r') as f:
            data = json.load(f)

        for item in data:
            if item.get('id') == self.__serverId:
                item['categories'] = list(self.__allowed)
                item['settings'] = self.__settings
    
        with open(self.JSONfileName, 'w') as f:
            json.dump(data, f, indent=4)
