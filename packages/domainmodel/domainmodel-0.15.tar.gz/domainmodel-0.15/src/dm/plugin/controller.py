import os, shutil

from dm.ioc import *
import dm.exceptions
from dm.dictionarywords import DB_MIGRATION_IN_PROGRESS
from threading import Condition

class PluginController(object):
    """Notifies plugins of domain model events. 'Observer (293)' [GoF, 1995]"""

    class __singletonPluginController(object):

        dictionary = RequiredFeature('SystemDictionary')
        registry = RequiredFeature('DomainRegistry')
        log = RequiredFeature('Logger')

        def __init__(self):
            self.plugins = None
            self.systems = {}
            self.notifyFifo = []
            self.isNotifying = False
            #self.condition = Condition()

        def notify(self, eventName, eventSender=None):
            """Notifies plugins of domain object events."""
            if self.dictionary[DB_MIGRATION_IN_PROGRESS]:
                return
            # Preserve order of events by putting them in a FIFO queue. Since
            # several plugins may handle an event, and since a handler may cause
            # further model events to be raised, it makes sense to allow each event
            # in turn to be fully handled by all plugins (avoids wierd cascades).
            msg = "PluginController: Adding '%s' event to notification queue." % eventName
            self.log.debug(msg)
            #self.condition.acquire()
            self.notifyFifo.append((eventName, eventSender))
            if self.isNotifying:
                #self.condition.release()
                msg = "PluginController: Notification queue is already running...."
                self.log.debug(msg)
            else:
                self.isNotifying = True
                #self.condition.release()
                try:
                    msg = "PluginController: Starting notification queue...."
                    self.log.debug(msg)
                    #self.condition.acquire()
                    while len(self.notifyFifo):
                        eventName, eventSender = self.notifyFifo.pop(0)
                        #self.condition.release()
                        try:
                            plugins = self.getPlugins()
                            msg = "PluginController: Notifying plugins of '%s' event." % eventName
                            #msg = 'PluginController: Notifying plugins %s ' % [p.domainObject.name for p in plugins]
                            #msg += 'of %s event from %s sender.' % (eventName, repr(eventSender))
                            self.log.debug(msg)
                            if eventName == 'PluginCreate':
                                self.onPluginCreate(eventSender)
                            if eventName == 'PluginDelete':
                                self.onPluginDelete(eventSender)
                            for plugin in plugins:
                                eventReceiverName = 'on' + eventName
                                if hasattr(plugin, eventReceiverName):
                                    eventHandler = getattr(plugin, eventReceiverName)
                                    if callable(eventHandler):
                                        self.log.debug("PluginController: Notifying the '%s' plugin of '%s' event." % (plugin.domainObject.name, eventName))
                                        eventHandler(eventSender)
                        except Exception, inst:
                            msg = "PluginController: Error notifying plugins of '%s' event: %s" % (eventName, inst)
                            self.log.error(msg)
                            raise
                        #finally:
                            #self.condition.acquire()
                    #self.condition.release()
                finally:
                    msg = "PluginController: Stopping notification queue...."
                    self.log.debug(msg)
                    #self.condition.acquire()
                    self.isNotifying = False
                    #self.condition.release()
        
        def onPluginCreate(self, pluginDomainObject):
            pluginSystem = pluginDomainObject.getSystem()
            if pluginSystem:
                pluginSystem.onCreate()
            self.plugins = None
            self.getPlugins()
        
        def onPluginDelete(self, pluginDomainObject):
            pluginSystem = pluginDomainObject.getSystem()
            if pluginSystem:
                pluginSystem.onDelete()
                if self.plugins != None and pluginSystem in self.plugins:
                    self.plugins.remove(pluginSystem)
        
        def getPlugins(self):
            p = list(self.registry.plugins)
            return [self.systems.get(i.name) or i.getSystem() for i in p]

    __instance = __singletonPluginController()

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

