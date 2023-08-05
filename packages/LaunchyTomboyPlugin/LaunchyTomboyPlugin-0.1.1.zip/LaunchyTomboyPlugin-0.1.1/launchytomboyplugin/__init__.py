import os.path as osp

import launchy
import launchytomboyplugin.lib as plib

class Tomboy(launchy.Plugin):
    def __init__(self):
        launchy.Plugin.__init__(self)
        self.tbl = plib.TomboyLib()
        self.name = self.tbl.name
        self.hash = launchy.hash(self.name)
        self.icon = self.tbl.icon
        self.tbl.debug_info()

    def init(self):
        pass

    def getID(self):
        return self.hash

    def getName(self):
        return self.name

    def getIcon(self):
         return self.icon

    def getLabels(self, inputDataList):
        pass

    def getResults(self, inputDataList, resultsList):
        pass

    def getCatalog(self, resultsList):
        self.tbl.debug('Adding Tomboy items to catalog')
        resultsList.push_back( launchy.CatItem(
            "Tomboy.NewNote",
            "Tomboy New Note",
            self.getID(),
            self.tbl.new_note_icon
        ))

        resultsList.push_back( launchy.CatItem(
            "Tomboy.Search",
            "Tomboy Search Notes",
            self.getID(),
            self.tbl.icon
        ))

        count = 0
        for title in self.tbl.note_titles:
            resultsList.push_back( launchy.CatItem(
                'Tomboy.Note.' + title,
                title,
                self.getID(),
                self.icon
            ))
            count += 1
        self.tbl.debug('Added {0} notes to catalog'.format(count))

    def launchItem(self, inputDataList, catItemOrig):
        catItem = inputDataList[-1].getTopResult()
        self.tbl.debug('Asked to launch:', catItem.fullPath)
        if catItem.fullPath == 'Tomboy.NewNote':
            self.tbl.new_note()
        elif catItem.fullPath == 'Tomboy.Search':
            self.tbl.search_notes()
        elif catItem.fullPath.startswith('Tomboy.Note.'):
            title = catItem.fullPath.replace('Tomboy.Note.', '', 1)
            self.tbl.launch_note(title)
        else:
            self.tbl.error('don\'t know how to launch:', catItem.fullPath)
