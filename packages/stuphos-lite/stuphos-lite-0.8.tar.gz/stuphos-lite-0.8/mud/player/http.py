# MUD Player HTTP Module.
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
HTTP_REDIRECT_MESSAGE = \
'''HTTP/1.0 302 Found
Location: %(location)s
Connection: close

No page content to render.
'''

HTTP_REDIRECT_VARS = dict(location = 'http://localhost/stuph/')
CON_CLOSE = 'Disconnecting'

def getHttpRedirectResponse():
    # date = 'Thu, 11 Feb 2010 18:18:44 GMT'
    vars = HTTP_REDIRECT_VARS.copy()

    # Ugh, this whole darn thing could come from config..
    from mud import getConfig
    url = getConfig('http-redirect-url') or ''
    url = url.strip()
    if url:
        vars['location'] = url

    response = HTTP_REDIRECT_MESSAGE % vars
    response = response.replace('\n', '\r\n')

    return response

def handleHttpRedirect(peer, (method, resource, protocol)):
    from mud import log as mudlog
    mudlog('HTTP LOGIN REDIRECT [%s]: %r' % (protocol, resource))

    # Send redirect response.  Disconnect.
    peer.write(getHttpRedirectResponse())
    peer.state = CON_CLOSE

    return True

def detectHttpRequest(peer, line):
    if peer.state != 'Get name':
        return False

    try: (method, resource, protocol) = line.split()
    except ValueError:
        return False

    if method.upper() not in ['GET', 'POST', 'OPTIONS', 'HEAD']:
        return False
    if not protocol.upper().startswith('HTTP'):
        return False

    return handleHttpRedirect(peer, (method, resource, protocol))
