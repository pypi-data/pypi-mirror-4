# Define verb commands (and others) based on mime message.
 #-
 # Copyright (c) 2013 Clint Banis (hereby known as "The Author")
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 # 1. Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 # 2. Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 # 3. All advertising materials mentioning features or use of this software
 #    must display the following acknowledgement:
 #        This product includes software developed by The Author, Clint Banis.
 # 4. The name of The Author may not be used to endorse or promote products
 #    derived from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS
 # ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 # TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 # BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 # CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 # SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 # INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 # CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 # ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #
# Note: this probably makes more sense as a wm structure, but it looks more formal this way.
from email import message_from_string, message_from_file

STUPH_CODE_TEXT = 'text/stuph-code'

class MessageDecoder:
    def __init__(self, msg):
        self.msg = msg

    def __getitem__(self, name):
        return self.msg[name]
    def getPayload(self):
        return self.msg.get_payload()

    def getAllOptions(self, key):
        return self.msg.get_all(key)
    def get(self, key, default = None):
        return self.msg.get(key, default)

class StuphCode(MessageDecoder):
    def evaluate(self, **values):
        languages = self['X-Coding-Language'].split(';')
        languages = dict((n.strip().lower(), True) for n in languages)

        def isLanguage(name):
            try: return languages.pop(name)
            except KeyError:
                return False

        if isLanguage('player-command'):
            minlevel = self.get('X-Command-Level')
            group = self.get('X-Command-Group')
            verb = self.get('X-Command-Verb')

            # Currently only supported language.
            assert len(languages) is 1
            assert 'python' in languages
            language = 'python'

            options = self.parseCommandOptions(self.getAllOptions('X-Command-Options'))
            options = list(options)

            return self.definePlayerCommand(verb, language, self.getPayload(),
                                            options = options,
                                            minlevel = minlevel,
                                            group = group)

        raise NameError(', '.join(languages.iterkeys()))

    def parseCommandOptions(self, options):
        # <short> | <long>
        # <option> =
        #   true|false [, <dest>]
        #   store [, <dest>]
        #
        # I'm beginning to think Todd Downey was right.
        from mud.player.commands import Option
        from mud.tools import splitOne

        for opt in options or []:
            (opt, defn) = splitOne(opt, '=')
            if defn:
                opt = opt.strip()
                defn = [n.strip() for n in defn.split(',')]

                short = len(opt) == 1
                opt = ('-' + opt) if short else '--%s' % opt

                assert defn
                ln = defn[0].lower()

                # Option parameters.
                if ln in ['true', 'false']:
                    action = 'store_' + ln
                    if not short and len(defn) == 1:
                        yield Option(opt, action = action)

                    assert len(defn) == 2
                    yield Option(opt, action = action, dest = defn[1])

                elif ln == 'store':
                    assert len(defn) == 2
                    yield Option(opt, dest = defn[1])

                else:
                    raise SyntaxError('Unknown definition for option %s: %s' % (opt, defn))

            else:
                # Simple storage option.
                yield Option(opt)

    def definePlayerCommand(self, verb, language, source, **kwd):
        # Invoke lambda-programming api.
        from mud.player.commands import programVerbCommand
        return programVerbCommand(verb, language, source, **kwd)

    class CommandBuilder:
        # Method chaining message builder.
        def __init__(self, verb = None, source = None, language = None):
            from email.message import Message
            self.msg = Message()
            self.msg.set_type(STUPH_CODE_TEXT)

            self.setVerb(verb)
            self.setSource(source)
            self.setLanguage(language)

        def __setitem__(self, name, value):
            self.msg[name] = value
        def setOnly(self, name, value):
            del self.msg[name]
            self[name] = value

        def setSource(self, source):
            if isinstance(source, (list, tuple)):
                source = '\n'.join(source)
            elif not source:
                source = ''

            self.msg.set_payload(source)
            return self

        def setVerb(self, verb):
            if verb:
                self.setOnly('X-Command-Verb', verb)

            return self

        def setLanguage(self, language):
            if language is None:
                language = 'python'
            else:
                assert language == 'python'

            self.setOnly('X-Coding-Language', 'player-command; ' + language)
            return self

        def setLevel(self, level):
            self.setOnly('X-Command-Level', level)
            return self

        def setGroup(self, group):
            self.setOnly('X-Command-Group', group)
            return self

        source = property(fset = setSource)
        verb = property(fset = setVerb)
        language = property(fset = setLanguage)
        level = property(fset = setLevel)
        group = property(fset = setGroup)

        def addOption(self, *args, **kwd):
            # Accepts regular add_option invocations and turns into X-Command-Option syntax.
            def _():
                for opt in args:
                    assert opt
                    if opt[0] == '-':
                        if len(opt) == 2:
                            opt = opt[1]
                        else:
                            assert len(opt) > 2 and opt[1] == '-'
                            opt = opt[2:]

                    action = kwd.get('action')
                    if action == ['store_true', 'store_false']:
                        opt = '%s=%s' % (opt, action[6:])

                        dest = kwd.get('dest')
                        if dest:
                            opt = '%s,%s' % (opt, dest)

                        yield opt

                    elif action:
                        dest = kwd.get('dest')
                        if dest:
                            yield '%s,%s' % (opt, dest)

                        yield opt

            for opt in _():
                self['X-Command-Option'] = opt

            return self

        # Message generation:
        def asString(self):
            return self.msg.as_string()
        def __str__(self):
            return self.asString()


# Todo: Runtime API.
MESSAGE_TYPE_EVALUTION = {STUPH_CODE_TEXT: StuphCode}
def loadMessage(msg, **kwd):
    V = MESSAGE_TYPE_EVALUTION[msg.get_content_type()]
    return V(msg).evaluate(**kwd)

def loadMessageString(string, **kwd):
    return loadMessage(message_from_string(string), **kwd)
def loadMessageFile(filename, **kwd):
    return loadMessage(message_from_file(filename), **kwd)


def testExample():
    '''
    MIME-Version: 1.0
    Content-Type: text/stuph-code
    X-Coding-Language: python; player-command
    X-Command-Level: implementor
    X-Command-Group: questing
    X-Command-Verb: do-this-*action
    X-Command-Option: v=true,verbose
    X-Command-Option: s=false,verbose
    X-Command-Option: verbose=true
    X-Command-Option: silent=false
    X-Command-Option: file-inputs
    X-Command-Option: f=store,file-inputs

    print '%r: %s' % (player, command)
    return True
    '''

    return StuphCode.CommandBuilder()                                          \
                    .setVerb('do-this-*action')                                \
                    .setLanguage('python')                                     \
                    .setLevel('implementor')                                   \
                    .setGroup('questing')                                      \
                    .addOption('-v', action = 'store_true', dest = 'verbose')  \
                    .addOption('-s', action = 'store_false', dest = 'verbose') \
                    .addOption('--verbose', action = 'store_true')             \
                    .addOption('--silent', action = 'store_false')             \
                    .addOption('--file-inputs')                                \
                    .addOption('-f', dest = 'file-inputs')                     \
                    .setSource(["print '%r: %s' % (player, command)",
                                "return True"])

# loadMessageString(str(testExample()))
