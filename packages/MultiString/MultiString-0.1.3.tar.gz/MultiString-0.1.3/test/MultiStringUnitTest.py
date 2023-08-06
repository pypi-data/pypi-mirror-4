from multistring import MultiString
import unittest
import base64
import os

class MSTestCase(unittest.TestCase):
    def setUp(self):
        self.multistring = MultiString("en","It's my turn!")

#    def tearDown(self):
        #print(self.multistring.__dict__)

    def testA(self):
        
        self.tstr = "It's my turn!"
       
        assert self.multistring.context == "en", "Expecting context 'en', was %s" % self.multistring.context
        assert self.multistring.active() == str(self.multistring), \
                "__str__ method failed."
        assert self.multistring.active() == self.tstr, \
                "Expecting value \"It's my turn!\", was %s" % self.multistring
        assert self.multistring.upper() == self.tstr.upper(), \
                "Resolution of str.upper() failed."

        self.multistring += " Now you."
        self.tstr += " Now you."

        assert self.multistring.active() == self.tstr, \
                "Concatenation operation failed."

        tlist = ["!","?"]
        tjoin = self.multistring.join(tlist)
        ejoin = self.tstr.join(tlist)

        assert tjoin == ejoin, "str.join() failed with %s" % tjoin

        self.multistring.addContext("de")
        self.multistring.active("de")

        assert self.multistring.context == "de", \
                "Active context not changed, is %s" % self.multistring.context

        self.tstr = "Ich bin an der Reihe!"

        assert self.multistring.active() is None, "Expecting None, %s returned" % self.multistring

        self.multistring.de = self.tstr

        assert self.multistring.__dict__['de'] == MultiString.CONTEXT, \
                "MultiString attribute 'de' is %s, should be %s" % (
                        self.multistring.__dict__['de'], MultiString.CONTEXT)

        assert self.multistring.__contexts__['de'] == self.tstr, \
                "Multistring Context not set as expected.\n\t'de' -> %s\n\t,tstr->%s" % (
                        self.multistring.__contexts__['de'],self.tstr)

        assert "de" in self.multistring.__contexts__, \
                "Despite other assertions, context 'de' not in: \t%s" % (self._multistring.__contexts__)

        assert self.multistring.de == self.tstr, \
                "Active context not returned as expected.\n\tde -> %s\n\ttstr->%s" % (
                        self.multistring.de,self.tstr)

        assert self.multistring.context == 'de', \
                "Context does not match activated context."

        assert self.multistring.de == self.multistring.active(), \
                "Active context result does not match active() return.\n\tde -> %s\n\tactive() -> %s" %(
                        self.multistring.de,self.multistring.active())

        self.tstr += " Jetzt dich."
        self.multistring += " Jetzt dich."

        assert self.multistring.active() == self.tstr, \
                "New context concatenation failed with %s" % self.multistring

        assert self.multistring.en != self.multistring.de, \
                "en != de failed!"

        self.t64str = base64.b64encode(self.multistring.en)
        self.tenstr = self.multistring.en
        self.tdestr = self.multistring.de
        self.multistring.addContext("b64", base64.b64encode(self.multistring.en))
        self.multistring.active('b64')

        assert self.t64str == str(self.multistring), \
                "Initial definition of b64 context failed."

        self.multistring.addTranslation('b64','en', lambda s: base64.b64decode(s))
        self.multistring.addTranslation('b64','de', lambda s: base64.b64decode(s))
        self.multistring.addTranslation('en','b64', lambda s: base64.b64encode(s))
        self.multistring.addTranslation('de','b64', lambda s: base64.b64encode(s))

        assert self.multistring.context == "b64", \
                "Active context should be 'b64', is %s" % self.multistring.context
        
        trx_b64en = self.multistring.translate('en')
        assert trx_b64en == self.tenstr, \
                "Translation from b64 -> en failed"

        self.multistring.active('de')
        trx_deb64_local = base64.b64encode(self.multistring.de)
        trx_deb64 = self.multistring.translate('b64', MultiString.OVERWRITE_STORED_VALUE)
        assert trx_deb64 == trx_deb64_local, \
                "Translation from de -> b64 failed"

        self.multistring.active('b64')
        trx_b64de = self.multistring.translate('de')
        assert trx_b64de == self.tdestr, \
                "Translation from b64 -> de failed"

        toverride = "Forced Translation"
        trx_b64en = self.multistring.translate('en', MultiString.OVERRIDE_TRANSLATION_PROTOCOL, lambda s: toverride)
        assert trx_b64en == toverride, \
                "Override of b64 -> en failed."

    def testMagic(self):

        assert self.multistring.active() == str(self.multistring), \
                "__str__ method not correctly implemented"

        curr = self.multistring.active()

        assert len(self.multistring) == len(curr), \
                "__len__ method not correctly implemented"

        add = curr + "junglebunny"
        madd = self.multistring + "junglebunny"
        assert add == madd, \
                "__add__ method not correctly implemented"

        radd = "junglebunny" + curr
        mradd = "junglebunny" + self.multistring
        assert radd == mradd, \
                "__radd__ method not correctly implemented"

        mul = curr*5
        assert (self.multistring*5) == mul, \
                "__mul__ method not correctly implemented"

        self.multistring.en  = "foo %s"
        assert (self.multistring % "bar") == "foo bar", \
                "Multistring not correctly passing format args with single format placeholder"

        self.multistring.en = "foo %s %s"
        assert (self.multistring %("bar","baz")) == "foo bar baz", \
                "MultiString not correctly passing multiple format arguments."

        tdict = {"one" : "bar", "two": "baz"}
        self.multistring.en = "foo %(one)s %(two)s" 
        assert (self.multistring % tdict) == "foo bar baz", \
                "MultiString not correctly processing format dicts."

    def testSlice(self):
        curr = self.multistring.active()
        assert(curr[:3] == self.multistring[:3]),\
                "Slicing improperly implemented."

    def testProperties(self):
        assert self.multistring.hasContext('en'), \
                "Expected 'True'"

        assert not self.multistring.hasContext('sp'), \
                "Expected 'False'"


        
    @unittest.expectedFailure
    def testF_InactiveContext(self):
        self.multistring.addContext('de', 'ich bin ein Berliner')
        self.active('de')
        self.multistring.en = self.tstr

    @unittest.expectedFailure
    def testF_RedefinedContext(self):
        self.multistring.addContext('en', self.tstr)

    @unittest.expectedFailure
    def testF_InvalidValueException(self):
        self.multistring.arbitrary = self.multistring.CONTEXT

    @unittest.expectedFailure
    def testF_TranslationNotFoundException(self):
        try:
            self.multistring.addContext('de', 'ich bin ein Berliner')
            self.multistring.active('en')
            fail = self.multistring.translate('de')
        except Exception as e:
            raise e
        finally:
            self.multistring.active('b64')

    @unittest.expectedFailure
    def testF_NullTranslation(self):
            self.addContext('b64')
            self.multistring.addTranslation('b64', 'en', lambda s: base64.b64encode(s))
            fail = self.multistring.translate('en')

    @unittest.expectedFailure
    def testF_ContextException(self):
        self.multistring.active('b65')

    @unittest.expectedFailure
    def testF_AttributeConflict(self):
        self.multistring.attrA = 42
        self.multistring.addContext('attrA','42')


if __name__ == "__main__":
    unittest.main()
