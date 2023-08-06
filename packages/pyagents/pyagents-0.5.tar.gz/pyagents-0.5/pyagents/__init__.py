import logging
root_logger = logging.getLogger('pyagents')
import inspect

class pyagentError(Exception): pass
class ScheduleError(pyagentError): pass

#TODO perhaps all action-instance pairs should be randomised
class Action(object):
    """A method to be executed on each provided instance of the given class"""

    def __init__(self, cls, method):
        self.cls = cls
        self.method = method
        self.logger = logging.getLogger('Action(%s.%s())' % (cls.__name__, method))

    def execute(self, instances):
        for instance in instances:
            if isinstance(instance, self.cls):
                self.logger.debug("executing on %s" % instance)
                method = getattr(instance, self.method, False)
                if method:
                    method()
        self.logger.debug("completed execution")

    def __repr__(self):
        return "Action(%s.%s())" % (str(self.cls), str(self.method))


#TODO: this is called both ActionSet and level - choose a name and stick with it
class ActionSet(object):
    """A set of actions to be run together"""
    def __init__(self, name):
        self.name = name
        self._actions = set([])
        self.logger = logging.getLogger('ActionSet(%s)' % name)

    def register_action(self, action):
        self._actions.add(action)

    def actions(self):
        for action in self._actions:
            yield action

    def execute(self, instances):
        for action in self._actions:
            self.logger.debug("executing %s" % action)
            action.execute(instances)


#TODO try to give it a more natural, list like interface - i.e. with []
class Schedule(object):
    """A schedule contains an ordered list of ActionSet objects"""
    def __init__(self, *names):
        self._levels = [ActionSet(name) for name in names]

    def register_level(self, name, index=None):
        if index is None:
            index = len(self._levels)
        self._levels.insert(index, ActionSet(name))

    def register_action(self, action, name):
        root_logger.info("Registering an action [%s, %s]" % (action, name))
        for level in self._levels:
            if level.name == name:
                level.register_action(action)
                return
        raise ScheduleError("level '%s' does not exist" % name)

    def execute(self, instances):
        """Execute each level in turn - they are ordered"""
        for level in self._levels:
            level.execute(instances)

def activate(**kwargs):
    """Create a decorator using the given kwargs"""
    root_logger.info("Creating a decorator with %s" % kwargs)

    def my_decorator(func):
        """Activate the decorated function to run at the given position in the schedule"""
        def wrapped(this):
            return func(this)
        wrapped.activated = kwargs
        return wrapped
    return my_decorator

class Activatable(object):
    """Base class for any object that can have its methods converted to actions"""
    @classmethod
    def activate(cls, schedule):
        """Add activated methods to the given schedule"""
        for method_name, method in inspect.getmembers(cls, predicate=inspect.ismethod):
            kwargs = getattr(method, 'activated', None)
            if not kwargs:
                continue
            try:
                level = kwargs['level']
            except KeyError:
                raise pyagentError, 'Must specify a priority level when activating a method'
            action = Action(cls, method_name)
            schedule.register_action(action, level)
        
class Agent(Activatable):
    pass
    
class Context(Activatable):
    pass
