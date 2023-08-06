## Table of Contents #

+ [What is MultiString?](#multistring)
+ [ChangeLog](#changelog)
+ [Creating a MultiString](#creation)
+ [String Usage](#stringusage)
+ [Contexts](#contexts)
+ [Translating](#translating)
  + [Defining Translations](#translating-defining)
  + [Translating Contexts](#translating-contexts)
+ [Context Access](#contextaccess)
+ [Gotchas](#gotchas)
+ [Why the Hell Would I Use This?](#whythehell)
+ [Testing](#testing)
+ [Installing](#installing)

<a name="multistring"></a>
# MultiString #
MultiString is a Python class which allows a single string to operate
in many different contexts. A good use case for this would be for the 
interchange of the same string in many different languages. 

The MultiString object itself can use any valid string method, and
the method will only affect the currently active context, meaning
MultiStrings can be used as-is with any existing code. Additionally,
MultiStrings are very protective of their contexts. An inactive context
may not be manipulated in any way, preventing you from accidentally
overwriting valuable information.

MultiStrings also offer bindings to translate contexts on the fly.

MultiStrings have full support for slicing and concatenation, and
even use the native `reversed` function, to return the string
backwards.

<a name="changelog"></a>
# Changelog #

+ 0.1.5:
    + Test suite now succeeds with both Py2.7 and Py3.2 (using Tox)
    + When initializing with a dict, may now pass in 'active' argument to set initial context
    + Fix initial string not being set if passed in by a user
    + Fix typo when raising NullValueException
    + Fix not building with pip

<a name="creation"></a>
# Creation #

When creating a MultiString, you must provide at least one context. 
You may also pass in defined translations for each context, if you wish.

There are four valid methods for creating a MultiString object:

    # Creates a MultiString with a single context, defines the context,
    # and sets this context as active
    basicMultiString = MultiString("en", "This is English")

    # Creates a MultiString with many contexts, and sets the first one 
    # as active
    stagedMultiString = MultiString(("en","de","sp")) 

    # Creates a MultiString with many contexts, defines the first one,
    # and sets the first one as active
    stagedWithDefault = MultiString(("en","de","sp"), "This is English")

    # Creates a MultiString with many contexts and defines them all,
    # but does not assume which you'd like set active
    fullyDefined = MultiString({
        "en"    :   "This is English",
        "de"    :   "Dieser is Deutsch",
        "sp"    :   "Este es el espanol"
    })

In all instances, the 'default' argument is optional (and will be ignored if you
pass in a dictionary). 

<a name="stringusage"></a>
# String Usage #

The MultiString does not inherit from the `str` class, but rather
defers to it whenever it needs help. If you try to call any method
that the MultiString class does not offer, it will attempt to call
that method on its currently active string itstead.

    multiString = MultiString("en", "this is english")
    multiString.upper() # returns 'THIS IS ENGLISH'
    multiString.upper() == multiString.en.upper()
    multiString += ", and here's another clause."
    print multiString # prints 'this is english, and here's another clause'

These operations _only_ affect the _active_ context. For instance:

    # assuming 'en' is still active
    multiString.addContext('de', 'Guten tag!')
    multiString += ". Also this."
    print multiString #prints "this is english. Also this."
    print multiString.en  #prints "this is english. Also this."
    print multiString.de #prints "Guten tag!"

This means that within the current context, you have normal control, but you 
will not affect any other context of the string. 

<a name="contexts"></a>
# Contexts #

Contexts are read-only unless they are active, and default to `None`.
Contexts may not be redefined later, and will throw an error if you try.
They also cannot be the same as any other attribute of the MultiString.
Again, this is for the protection of your data!

    multiString = MultiString(('en','de'),"This is English.")
    multiString.addContext('en', "Woops!")      # error. Context already exists.
    multiString.de = "Deutsch!"                 # error, because 'en' is active
    multistring.en = "This is cool, though."    # fine, because we're manipulating the active context
    print(multiString.de)                       #'None'
    multiString.someProperty = 17               # no problem!
    multiString.someProperty = 29               # no problem!
    multiString.addContext('someProperty')      # error! You'll be sorry!

<a name="translating"></a>
# Translating #

The last feature of the MultiString is native translation. 

<a name="translating-defining"></a>
## Defining Translations  #

You can add translations between any two defined contexts. You must provide
three arguments to the `addTranslation` method: 

    addTranslate(fromContext,toContext,callback)

where `callback` is a function reference or lambda which _accepts_ a 'from' and _returns_ a 'to'

    import base64

    multiString = MultiString(('en','b64'))
    multiString.addTranslation('en','b64', lambda s: base64.b64encode(s))
    multiString.addTranslation('b64','en', lambda s: base64.b64decode(s))

<a name="translating-contexts"></a>
## Translating Contexts #

Translating always occurs from the active context, to whatever context
you provide. When translating, you also have options to store these translations,
or override the translation protocol for special circumstances.

    multiString.active('en')
    multiString.en = "Here is some English"

    # Two things happen here. Since the 'b64' context is currently empty,
    # it will store the translation in the 'b64' context, as well as return it.
    en_to_b64 = multiString.translate('b64')
    en_to_b64 == multiString.b64 # True

    # However, if we change the english and run another translation,
    # the result will not be preserved by default, in order to prevent you
    # from losing data:

    multiString.en = "Some other English"
    en_to_b64 = multiString.translate('b64')
    en_to_b64 == multiString.b64 # False

    # You can override this default behaviour:
    en_to_b64 = multiString.translate('b64', OVERWRITE_STORED_VALUE)
    en_to_b64 == multiString.b64 # True

    # You can also perform an on-the-fly translation through some other 
    # means, so long as the destination context is previously defined.
    en_to_b64 = multiString.translate('b64', OVERRIDE_TRANSLATION_PROTOCOL, lambda s: "Just kidding!")
    en_to_b64 == multiString.b64 # False
    en_to_b64 = multiString.translate('b64', OVERRIDE_TRANSLATION_PROTOCOL | OVERWRITE_STORED_VALUE, lambda s: "Just kidding!")
    en_to_b64 == multiString.b64 # True

    # The last thing we can do is skip the 'addTranslation' step altogether. If no translation exists
    # for this context, the translation will be added automatically if you provide it:

    multiString.en = "Here's some letters and numbers: ABCDEF4815162342"
    multiString.addContext('letters')
    letters = multiString.translate('letters', callback=lambda s: "".join([char for char in s if char in string.ascii_letters]))
    letters == multiString.letters # True
    letters == "HeressomelettersandnumbersABCDEF" # True

    multiString.addContext('only8')
    multiString.active('letters')
    multiString.translate('only8', callback=lambda s: s[:8]) # == "Heressom"
    multiString.active('en')
    multiString.translate('only8') # == 'Here's S'

<a name="contextaccess"></a>
# Context Access #

Contexts can be read as would any other property of a class. 

    multiString.addContext('foo', 'bar')
    print multiString.foo # 'bar'
    
You can get the active context using the 'str' method, or the 'active()' method:

    multiString.active() == str(multiString) # True

<a name="gotchas"></a>
# Limitations & Gotchas #

Because Python tags values, and doesn't 'set variables', you cannot alter your active context
simply by assigning the multiString another value.

    multiString = MultiString('en', "Hello, World!")
    multiString = "Goodbye, cruel world!" # No! Your MultiString will be destroyed

Instead, you must assign the context itself (and only the active one, at that):

    multiString = MultiString('en', "Hello, World!")
    multiString.en = "Goodbye, cruel world!" # Much better

The `str()` method will always refer to the _active_ context. This is intended behaviour. However, you
may call this method on other contexts with the dot operator:

    multiString.active('en')
    str(multiString) == multiString.en # True
    str(multiString.de) == multiString.de # True, if 'de' is not None

    print(multiString) # prints the active context

Because the MultiString defers to native string methods as much as it can to allow
drop in support of MultiString objects into current code, it can be difficult to 
access MultiString properties themselves, as they are masked by their `str` counterparts.

<a name="whythehell"></a>
# Why the Hell Would I Use This? #

If you have a system which is being translated into other languages, the MultiString can be a valuable method
of replacing syntax without having to rewire your entire system. For instance:

__Old System__:

    errorMessage = "Sorry, but something went horribly wrong and you should give up now!\n"
    sys.stderr.write(errorMessage)

That's only useful if your audience speaks English.

__Enter the MultiString__:

    errorMessage = MultiString({
        "en"        :   "All praise the great one! Let him rise and weave us new dreams!",
        "piglatin"  :   "Allyay raisepay ethey ategray oneyay!"
        "cthulian"  :   "Ia! Ia! Cthulhu fhtaghn!"
    })

    errorMessage.active(user.preferred_language)

    sys.stderr.write(errorMessage + "\n")

__External APIs__:

If you wanted, you could also seamlessly integrate another API to natively handle translations for you:

    multi = MultiString(('en','es'), "I don't speak Spanish, but Google kinda does.")
    multi.addContext(user.preferred_language)

    # Assuming you have an api with a method 'sendCall' which takes 
    # a language code and some text as arguments
    multi.translate(user.preferred_language, lambda s: someAPI.sendCall(user.preferred_language, multi.active()))
    multi.active(user.preferred_language)
     

__Computer Science__:

This is what the MultiString was originally conceived for, by the way:

    multi = MultiString(('py','cpp'))
    multi.addTranslation('py','cpp', myPyToCppModule)
    multi.addTranslation('cpp','py', myCppToPyModule)
    multi.py = "print(Hello world!)"
    multi.translate('cpp') # returns 'std::cout <<< "Hello world!" << std::endl;'
    multi.active('cpp')
    multi.translate('py') == multi.py # True if the translation modules were written correctly

<a name="testing"></a>
# Testing #

If you're on python 2.7.3 or higher, you can run 'python MultiStringUnitTest.py' to 
run basic tests. Please let me know if any of them fail, or you find anything else that the
tests don't cover, but should!

<a name="installing"></a>
# Installing #

There is no installation required. Since this is a single class, you can simply import it as-is.
However, if you wish to install it on your python's Path, you can do so with
   
    python setup.py install
    # OR
    easy_install MultiString 
    # OR
    pip install MultiString 

Regardless:  `from multistring import MultiString` will get you up and running.

There are no variables outside of the class scope that will affect your namespace.

<a name="license"></a>
# License #

__MultiString is distributed with GPLv3__

MultiString - A String class that allows strings to have contextual meanings
Copyright (C) 2013 - Tom A. Thorogood

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

<a name="credits"></a>
# Credits #

[Tom A. Thorogood](http://www.github.com/tomthorogood)
[Jonathan Eunice](http://www.github.com/jonathaneunice)
