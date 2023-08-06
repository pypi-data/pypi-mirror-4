
class Explore(object):
    """
    Util for traversing a service tree.
    """
    @classmethod
    def walk(cls, service):
        """
        Walk over the given service(s) and subservices.
        """
        # Param can be a list of services.
        if isinstance(service, (list, tuple)):
            todo = service[:]
        else:
            todo = [service]

        visited = set()

        while todo:
            s = todo.pop()
            yield s
            visited.add(s)

            for name, subservice in cls.get_subservices(s, include_isolations=False):
                if name != 'root' and subservice not in visited:
                    todo.append(subservice)

        @classmethod
        def get_subservices(self, service, include_isolations=False, include_proxies=False):
            pass

        @classmethod
        def

# ------------

class Service(object):
    __slots__ = ('env', )

    def __init__(self, env):
        self._env = env

class VikingSpots(Service):
    class Hosts:
        pass

class VikingSpots(Service):
    class Meta:
        group = ...

    class Hosts: # HostsContainer
        default = [ ... ]

    class Env:
        pty = ...


    parent = Parent # ... Filled in dynamically by descriptor.
    creator_service = CreatorService # ... Filled in dynamically by descriptor.
    root = RootService # ... Filled in dynamically by descriptor.

    @map_roles('www', k='v')
    class django(IsolatedService):
        class Hosts:
            default = []

        class Meta:
            role_mapping = map_roles()


s = Service(env=DefaultEnv())

with env.sandbox():
    s.django.shell_plus()


class Action(object):
    def __call__(self


    self.hosts.filter('...').run(...)

