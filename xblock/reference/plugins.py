import json

from djpyfs import djpyfs

from xblock.fields import Field, NO_CACHE_VALUE
from xblock.fields import Scope, UserScope, BlockScope

## Finished services (this space intentionally left blank)







## edX-internal prototype services


## TODO: Move somewhere useful. 
## TODO: Clean up how key is generated
## TODO: Include field name, if not there yet? 
def scope_key(instance, xblock):
    dict = {}
    if instance.scope.user == UserScope.NONE or instance.scope.user == UserScope.ALL:
        pass
    elif instance.scope.user == UserScope.ONE:
        dict['user'] = xblock.scope_ids.user_id
    else:
        raise NotImplementedError()

    if instance.scope.block == BlockScope.TYPE:
        dict['block'] = xblock.scope_ids.block_type # TODO: Is this correct? Was usage_id
    elif instance.scope.block == BlockScope.USAGE:
        dict['block'] = xblock.scope_ids.usage_id # TODO: Is this correct? was def_id. # Seems to be the same as usage? 
    elif instance.scope.block == BlockScope.DEFINITION:
        dict['block'] = xblock.scope_ids.def_id
    elif instance.scope.block == BlockScope.ALL:
        pass
    else: 
        raise NotImplementedError()

    basekey = json.dumps(dict, sort_keys = True, separators=(',',':'))
    def encode(s):
        if s.isalnum():
            return s
        else:
            return "_{}_".format(ord(s))
    encodedkey = "".join(encode(a) for a in basekey)

    return encodedkey


def public(**kwargs):
    ''' Mark a function as public. In the future, this will inform the XBlocks services 
    framework to make the function remotable. For now, this is a placeholder. 

    The kwargs will contain: 

      type : A specification for what the function does. Multiple
      functions of the same type will have identical input/output
      semantics, but may have different implementations. For example,

        type = student_distance

      Takes two students and returns a number. Specific instances may
      look at e.g. difference in some measure of aptitude, geographic
      distance, culture, or language. See stevedor, as well as queries
      in https://github.com/edx/insights to understand how this will
      be used.
    '''
    def wrapper(f):
        return f

    return wrapper


class Service(object):
    ''' Top-level definition for an XBlocks service. 
    This is intended as a starting point for discussion, not a finished interface. 

    Possible goals: 

    * Right now, they derive from object. We'd like there to be a common superclass. 
    * We'd like to be able to provide both language-level and service-level bindings. 
    * We'd like them to have a basic knowledge of context (what block they're being 
      called from, access to the runtime, dependencies, etc.
    * That said, we'd like to not over-initialize. Services may have expensive 
      initializations, and a per-block initialization may be prohibitive. 
    * We'd like them to be able to load through Stevedor, and have a plug-in 
      mechanism similar to XBlock. 

    This superclass should go somewhere else. This is an interrim location until we
    figure out where. 
    '''
    def __init__(self, context):
        # TODO: We need plumbing to set these
        self._runtime = context.get('runtime', None)
        self._xblock = context.get('xblock', None)
        self._user = context.get('user', None)

    def xblock(self):
        return self._xblock

    def runtime(self):
        return self._runtime


class FSService(Service):
    ''' This is a PROTOTYPE service for storing files in XBlock fields. 

    It returns a file system as per:
      https://github.com/pmitros/django-pyfs

    1) The way this service is initialized and used is likely
    wrong. We'll want to fix it.
    2) There is discussion as to whether we want this service at
    all. Specifically:
    - It is unclear if XBlocks ought to have filesystem-as-a-service, 
      or just as a field, as per below. Below requires an FS service, 
      but it is not clear XBlocks should know about it. 

    - It is unclear if pyfilesystem has performance properties we
      want.  Our goal is to try this in a limited roll-out, and see if
      whether we run into limitations, and if so, which ones. This is
      not intended as part of the XBlock standard until we've built up
      more experience and comfort with it. See: 

      https://groups.google.com/forum/#!topic/edx-code/4VadWwqeMNI
    '''

    @public()
    def load(self, instance, xblock):
        # TODO: Get xblock from context, once the plumbing is piped through
        return djpyfs.get_filesystem(scope_key(instance, xblock))
    
    def __repr__(self):
        return "File system object"


class Filesystem(Field):
    '''
    An enhanced pyfilesystem.

    This returns a file system provided by the runtime. The file
    system has two additional methods over a normal pyfilesytem: 
    1) get_url allows it to return a reference to a file on said
    filesystem
    2) expire allows it to create files which may be garbage 
    collected after a preset period. 

    This is a PROTOTYPE intended for limited roll-out. See comments 
    in FSService above. 
    '''
    MUTABLE = False

    def __get__(self, xblock, xblock_class):
        """
        Gets the value of this xblock. Prioritizes the cached value over
        obtaining the value from the _field_data. Thus if a cached value
        exists, that is the value that will be returned. Otherwise, it 
        will get it from the fs service. 
        """
        # pylint: disable=protected-access
        if xblock is None:
            return self

        value = self._get_cached_value(xblock)
        if value is NO_CACHE_VALUE:
            value = xblock.runtime.service(xblock, 'fs').load(self, xblock)
            self._set_cached_value(xblock, value)

        return value

    def __delete__(self, xblock):
        ''' We don't support this until we figure out what this means '''
        raise NotImplementedError

    def __set__(self, xblock, value):
        ''' We don't support this until we figure out what this means '''
        raise NotImplementedError
