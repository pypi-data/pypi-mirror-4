# Try Google ipaddr module.
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
try: import ipaddr as google_ipaddr
except ImportError:
    def _parse_ip(addr):
        return None
else:
    # Otherwise, such ip structures aren't supported.
    def _parse_ip(addr):
        try: return google_ipaddr.IP(addr)
        except ValueError:
            return None

def _parse_valid_ips(args):
    # Todo: unroll expression this into a generator function.
    return (a if ip is None else ip \
            # Provide parsed ip structure or string.
            for (a, ip) in \
                ((a, _parse_ip(a)) \
                 for a in args) if \
                 ip is not None or type(a) is str)

class IPAddressGroup(list):
    def __contains__(self, host):
        if type(host) is str:
            hostip = _parse_ip(host)
            for ip in self:
                if type(ip) is str:
                    if host == ip:
                        return True

                elif hostip in ip:
                    return True

        return False

    # Todo: provide explicit ranges?

    def __init__(self, *args):
        list.__init__(self, _parse_valid_ips(args))

    def add(self, address):
        if address not in self:
            self.append(address)
