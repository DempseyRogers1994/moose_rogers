# Writing an extension from scratch
import os, re
import pickle
import logging
from ..tree import tokens
from ..common import __init__, exceptions
from . import command
import json
import codecs
from threading import Thread, Event, Lock, current_thread
from TestHarness.schedulers.Scheduler import Scheduler as s
from  ..base import executioners as ex
from  ..base import Translator as tr
import uuid


"""     Tagger ouputs to tags.txt found at: 'moose/python/MooseDocs/extensions'

        This extension defines the tagger command: !tagger name path key:value.  Tagger will except a string that represents the markdown file that is associated with an arb. list of key:value pairs.
        Arb spacing is allowed after the name/markdown name, however only one space is allowed before the name/markdown.  Ex: !tagger name    k1:v1  ka:va thing1:thing2 is okay, but not
        !tagger  name.

        Tagger checks that all linked moose pages are unique and will not allow duplicate namess in the dictionary.  Duplicate key value pairs are allowed.

        If moose is served and *.md is editied to change an existing !tagger command, recompiling will NOT pick up the change since the moose page is already in the dictionary.  To fix this rm tags.txt found
        in the 'moose/python/MooseDocs/extensions' and create a new one: vim tags.txt.  After compiling with the empty txt the changes will be up dated. Probably a best practice to do this before using the
        pkl to generate the database filtering system.

        Since tagger & database happen before moose is served !tagger in *.md must be saved before ./moosedocs.py build --serve for the name to appear in the database filtering system. However, saving
        *.md with new !tagger will add it to the tags.txt.

        Example Tagger command in *.md:
        !tagger geochem keyg:valg keychem:valuechem

        Example Output TagDictionary in tags.txt:
        {"data":
        [{"name": "heatconduction", "path": "moose/modules/heat_conduction/doc/content/modules/heat_conduction/index.md", "key_vals": {"keyheat": "valheat", "key": "val", "key1": "val1"}},
        {"name": "index", "path": "moose/modules/doc/content/index.md", "key_vals": {"key1": "val1", "keya": "val"}},
        {"name": "index2", "path": "moose/modules/doc/content/index2.md", "key_vals": {"key1": "val1", "keya": "val", "thing1": "thing2"}},
        {"name": "geochem", "path": "moose/modules/geochemistry/doc/content/modules/geochemistry/index.md", "key_vals": {"keyg": "valg", "keychem": "valuechem"}},
        {"name": "vortex", "path": "moose/modules/level_set/doc/content/modules/level_set/example_vortex.md", "key_vals": {"keyvor": "valvor", "key": "val", "key1": "val1"}}]
        }  """

LOG = logging.getLogger(__name__)

def make_extension(**kwargs):  #reqired extension
    return TaggingExtension(**kwargs)

TaggingToken = tokens.newToken('TaggingToken', brand='')
TaggingTitle = tokens.newToken('TaggingTitle', brand='', prefix=True, center=False, icon=True, icon_name=None)
TaggingContent = tokens.newToken('TaggingContent')

class TaggingExtension(command.CommandExtension):
    # Threading changes - make self accessable to all threads to allow .join of .database
    
    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        return config

    def extend(self, reader, renderer):
        self.requires(command)
        self.addCommand(reader, TaggingCommand())
    def __init__(self, *args, **kwargs):
        command.CommandExtension.__init__(self, *args, **kwargs)
        self._database={'data':[]}
        self.__executioner = ex.Executioner(**kwargs)
        self.__parallellBarrier=ex.ParallelBarrier()
        self.__parallellQueue=ex.ParallelQueue()
        self.__parallellPipe=ex.ParallelPipe()
        self.__unique_id = uuid.uuid4()      # a unique identifier
    @property
    def database(self):
        return self._database
    @property
    def executioner(self):
        """Return the Executioner object."""
        return self.__executioner
    @property
    def parallelbarrier(self):
        """Return the Executioner object."""
        return self.__parallellBarrier
    @property
    def parallelqueue(self):
        """Return the Executioner object."""
        return self.__parallellQueue
    @property
    def parallelpipe(self):
        """Return the Executioner object."""
        return self.__parallellPipe
    @property
    def uid(self):
        """Return the unique ID for this translator object."""
        return self.__unique_id
    
    def addTag(self, page):
        """Add an additional page to the list of available pages."""
        self.__executioner.addTag(page)

    def addTags(self, tags):
        """Add an additional pages to the list of available pages."""
        for tag in tags:
           self.__executioner.addTag(tag)

    def initTags(self, tag):
        """Initialize a page (call after addPage)."""
        if not self.__initialized:
            msg = "`initTags` should only be done after the Translator.init()"
            raise exceptions.MooseDocsException(msg)
        self.__executioner.initTags([tag])

    def getTags(self):
        """Return the Page objects"""
        return self.__executioner.getTags()
    
class TaggingCommand(command.CommandComponent):
    COMMAND= 'tagger'
    SUBCOMMAND= '*'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        return settings
    
    def _lock(self):
        # with self.extension.executioner._ctx.Lock():
        self._lock = self.extension.executioner._ctx.Lock()
        return self._lock

        
    

    def createToken(self, parent, info, page, settings):
        print(f"\ncurrent thread name {current_thread().name}")
        a=ex.Executioner.setGlobalAttribute(self, 'tagging', tags)
        print('\nsetGA')
        print(a)
        # self.extension.executioner._lock
        with self._lock():
            # a=ex.Executioner.setGlobalAttribute(self, 'tagging', tags)
            # print('\nsetGA')
            # print(a)
            allowedKeys=['key1', 'keya', 'keyx', 'thing1', 'keyg']
            name=info[2]
            keylist=info[3].split()
            mpath=re.sub(r'^.*?moose/', 'moose/', page.source)
            EntryKeyValDict=[]
            for keys in keylist:
                key_vals=keys.split(':')
                EntryKeyValDict.append([key_vals[0],key_vals[1]])

            PageData= {'name':name, "path":mpath, "key_vals":dict(EntryKeyValDict)}

            self.extension.database['data'].append(PageData)
            
            for i in range(len(self.extension.database['data'])):
                bad_keys=[]
                for key in self.extension.database['data'][i]['key_vals'].keys():
                    if key not in allowedKeys:
                        bad_keys.append(key)

                if len(bad_keys)>0:            
                    msg = "Not and allowed key; not adding to 'key' dictionary: "
                    msg += ", ".join(bad_keys)
                    LOG.warning(msg)
                for key in bad_keys:
                    del self.extension.database['data'][i]['key_vals'][key]
                self.extension.executioner.addTag(self.extension.database['data'][i])
            
            tags=self.extension.executioner.getTags()
            print('\ngetTags')
            print(tags)
            
            # a=ex.Executioner.setGlobalAttribute(self, 'tagging', tags)
            # print('\nsetGA')
            # print(a)


            # b=(ex.Executioner.getGlobalAttribute(self, current_thread().name))
            # print('\ngetGA')
            # print(b)

            print('\ntagObj')
            print(self.extension.executioner._tagging_objects)
        
        # print(self.extension.parallelpipe._translator)

        # content= self.extension.parallelpipe(self.extension.executioner)
        # print(content)
# 
#-----------------------------------------------------------
        # if (platform.python_version_tuple()[0] >= '3') and (int(platform.python_version_tuple()[1]) >= 9) and (platform.system() == 'Darwin'):
        #     self._ctx = multiprocessing.get_context('fork')
        # else:
        #     self._ctx = multiprocessing.get_context()

        # # A lock used prior to caching items or during directory creation to prevent race conditions
        # self._lock = self._ctx.Lock()

        # ex.Executioner(self.extension.addTag(PageData))
        # ex.Executioner.addTag(self, PageData)
        # ex.Executioner.setGlobalAttribute(self,key='data', value=PageData)
        # print(ex.Executioner.getGlobalAttribute(self,key='data'))
        # return info
    