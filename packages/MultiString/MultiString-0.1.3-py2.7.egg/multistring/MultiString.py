
class MultiString(object):
    """
    A MultiString holds multiple values that vary contextually.
    When manipulating a MultiString, only the 'active' context
    is manipulated. By default, the first context given is the
    active context. 

    Contexts are directly accessible with the dot operator, but
    are not implicitly changeable. In order to be changed, they
    must be made active.

    MultiStrings otherwise behave as strings.

    """
    CONTEXT = "__MultiStringContextObject__"
    
    OVERRIDE_TRANSLATION_PROTOCOL = 1
    OVERWRITE_STORED_VALUE = 2
    
    class InactiveContextException(Exception):
        def __init__(self, context, active):
            self.context = context
            self.active = active
        def __str__(self):
            return "Cannot alter inactive context %(context)s, %(active)s currently active." % self.__dict__

    class RedefinedContextException(Exception):
        def __init__(self, context, existing, attempt):
            self.context = context
            self.existing = existing
            self.attempt = attempt

        def __str__(self):
            return "Cannot define context %(context)s as %(attempt)s. Already defined as %(existing)s." % self.__dict__

    class InvalidValueException(Exception):
        def __init__(self, attr):
            self.attr = attr
        def __str__(self):
            return "You are trying to do something very fishy. An arbitrary value may not be \"%s\". Clearly you've read the code and are trying to break it. STAHP." % self.attr

    class TranslationNotFoundException(Exception):
        def __init__(self,orig,dest):
            self.orig = orig
            self.dest = dest
        def __str__(self):
            return "No translation found from %(orig)s to %(dest)s" % self.__dict__

    class NullTranslationException(Exception):
        def __init__(self,context):
            self.context = context

        def __str__(self):
            return "Cannot translate %(context)s because it currently has no value." % self.__dict__

    class ContextException(Exception):
        def __init__(self,context):
            self.context = context
        def __str__(self):
            return "Cannot interact with non-existent context %(context)s" % self.__dict__

    class AttributeConflictError(Exception):
        def __init__(self, attr, val):
            self.attr = attr
            self.val = val
        def __str__(self):
            return "Attempt to add context %(attr)s failed, because it is already a property of this object, containing the value %(val)s" % self.__dict__

    def __init__(self, contexts, initstr=None, active=None):
        """
        ms = MultiString({'en' : 'hello', 'sp' : 'hola'})
        ms = MultiString(('en','sp'),'hello')
        """
        self.__dict__["__contexts__"] = {}
        self.__dict__["context"] = None
        self.__dict__["__trx__"] = {}
        
        if isinstance(contexts,dict):
            # Note that in dict instances, we cannot assume an 
            # initial context.
            self.importDict(contexts)
            if active is not None:
                self.active(active)
        elif isinstance(contexts,(list,tuple)):
            self.importList(contexts)
            self.active(contexts[0])
            self.__contexts__[contexts[0]] = initstr
        elif isinstance(contexts,str):
            self.addContext(contexts,initstr)
            self.active(contexts)
            self.__contexts__[contexts] = initstr


    def __setattr__(self,attr,value):
        """
        Ensures that strings contexts cannot be accidentally overwritten through
        the dot operator.

        ms.addContext('foo')
        ms.foo = "Hello" #valid
        ms.foo = "Goodbye" #error

        ms.addContext('bar','Hello') #valid
        ms.bar = 'Goodbye' #error

        ms.arbitraryAttr = 0x19 #valid
        """
        if attr in self.__contexts__:  
            if self.context != attr:
                raise MultiString.InactiveContextException(attr,self.context)
            else:
                self.__contexts__[attr] = value

        elif value == MultiString.CONTEXT:
            raise MultiString.InvalidValueException(attr)
        else:
            self.__dict__[attr] = value

    def __getattribute__(self,name):
        
        def attr(name):
            return object.__getattribute__(self,name)

        def isContext(name):
            c = attr('__contexts__')
            return name in c

        def context(name):
            c = attr('__contexts__')
            return c[name]

        if name == "__dict__":
            return attr("__dict__")

        if isContext(name):
            return context(name)
        else:
            try:
                return attr(name)
            except AttributeError:
                try:
                    return self.active().__getattribute__(name)
                except AttributeError as e:
                    raise e



    def __str__(self):
        """
        Returns the active string.
        """
        return self.active()

    def __iadd__(self,other):
        if not isinstance(other,(str,MultiString)):
            raise TypeError
        if isinstance(other,str):
            self.__contexts__[self.context] += other
        elif isinstance(other,MultiString):
            self.__contexts__[self.context] += str(other)
        return self

    def __add__(self,other):
        if isinstance(other,str):
            return self.active() + other
        elif isinstance(other,MultiString):
            return self.active() + other.active()

    def __radd__(self,other):
        if isinstance(other,str):
            return other + self.active()
        elif isinstance(other,MultiString):
            return other.active() + self.active()

    def __mul__(self,num):
        return self.active() * num

    def __len__(self):
        return len(self.active())

    def __unicode__(self):
        return self.active().encode("utf8")

    def __reversed__(self):
        return self.active()[::-1] 

    def __contains__(self, other):
        return other in self.active()

    def __getitem__(self,other):
        return self.active()[other]

    def __cmp__(self,other):
        if self.active() < other:
            return -1
        elif self.active() == other:
            return 0
        else:
            return 1

    def __ne__(self,other):
        return self.active() != other

    def __nonzero__(self):
        return self.active() is not None

    def __mod__(self, *args):
        if len(args) is 1:
            return self.active() % args[0]
        else:
            return self.active() % args

    def __repr__(self):
        """
        Returns the active string.
        """
        return repr(self.active())

    def importList(self,contexts):
        """
        Context lists provide context names without defining them.
        This is perfectly valid behaviour.
        """
        for context in contexts:
            self.addContext(context)

    def importDict(self,contexts):
        """
        Context dictionaries define both context names and their initial definitions.
        """
        for context in contexts:
            definition = contexts[context]
            self.addContext(context,definition)

    def translate(self, destination, flags = 0, callback=None):
        """
        Attempts to translate from one context to another.
        If the destination context has not already been set, this
        will do that also. If the destination context is already
        set within this instance, the translation will not be
        stored by default.

        Likewise, you may pass in the translation callback (see addTranslation)
        with this method, however if that protocol has already been set, the
        value passed here will be ignored.

        These defaults can be overridden with flags:
            OVERWRITE_STORED_VALUE 
                will overwrite the destination context with the translation,
                even if it already exists.
            OVERRIDE_TRANSLATION_PROTOCOL 
                will use the provided callback passed into this method, instead
                of the one stored in the translation dictionary. The passed
                translation will NOT be stored. To store it, use the 
                'addTranslation' method instead.

        ms.addContext('fwd','Hello')
        ms.addContext('bkwd')
        ms.active('fwd')
        ms.translate('bkwd', callback=lambda f: f[::-1]) # returns 'olleH'
        ms.active('bkwd')
        ms.translate('fwd', callback=lambda f: f[::-1]) # return 'Hello')
        ms.active('fwd')
        ms.translate('bkwd') # returns 'olleH'
        ms.translate('bkwd', ms.OVERWRITE_STORED_VALUE | ms.OVERRIDE_TRANSLATION_PROTOCOL, lambda f: '!'*len(f))
            # returns '!!!!!', and stores it.
        ms.translate('bkwd', OVERWRITE_STORED_VALUE)
            # returns 'elloH' and stores it.
        """
        trx = None

        # If the translation has not been added, but a method was provided, 
        # attempt to add the translation to the trx dictionary
        if self.context not in self.__trx__ \
            or destination not in self.__trx__[self.context]:
            if callback:
                self.addTranslation(self.context,destination,callback)
            else:
                raise MultiString.TranslationNotFoundException(self.context,destination)
        # Cannot translate 'None' or ""
        elif self.active() in (None,""):
            raise MultiString.NullTranslationException(self.active())
        
        # Determine translation protocol 
        if callback and (flags & MultiString.OVERRIDE_TRANSLATION_PROTOCOL):
            trx = callback
        else:
            trx = self.__trx__[self.context][destination]


        translation = trx(self.active())

        # Write new values, or seek permission to overwrite values
        if (self.__contexts__[destination] is None) or (flags & MultiString.OVERWRITE_STORED_VALUE):
            self.__contexts__[destination] = translation

        return translation

    def addTranslation(self,originalContext,destinationContext,callback):
        """
        Provides a way of converting from one context to another. 
        The callback must be a function that takes 'originalContext' and returns
        'destinationContext'.

        Errors will be thrown if either context does not exist, or
        if the callback is not a valid function.
        """
        if originalContext not in self.__contexts__:
            raise MultiString.ContextError(originalContext)
        if destinationContext not in self.__contexts__:
            raise MultiString.ContextError(destinationContext)
        if not hasattr(callback,'__call__'):
            raise AttributeError

        if originalContext not in self.__trx__:
            self.__trx__[originalContext] = {}
        self.__trx__[originalContext][destinationContext] = callback
        
    def addContext(self, context, value=None):
        """
        A context can have any name, as long as that name is a valid python identifier.
        The name cannot already exist as a context or a property of the object.

        ms.foo = 17 # ok
        ms.addContext('foo','hello') # error
        ms.addContext('bar') # ok
        ms.addContext('bar','hello') # error
        """
        if context in self.__contexts__:
            raise MultiString.RedefinedContextException(context,self.__contexts__[context],value)
        elif context in self.__dict__:
            raise MultiString.AttributeConflictError(context,self.__dict__[context])
        self.__contexts__[context] = value
        self.__dict__[context] = MultiString.CONTEXT

    def active(self,context=None):
        if not context:
            try:
                return self.__contexts__[self.context]
            except KeyError:
                raise MultiString.ContextException(context)
        
        if context not in self.__contexts__:
            raise MultiString.ContextException(context)
    
        self.context = context

    def hasContext(self,context):
        return context in self.__contexts__
