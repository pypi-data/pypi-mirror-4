"""
implements (nominally) the grammar from RFC2616 and RFC2617
using pyparsing
"""

from pyparsing import *

# rfc 2616 defines Notational Conventions and Generic Grammar used in
#  rfc 2617. http://www.w3.org/Protocols/rfc2616/rfc2616-sec2.html#sec2.1

"""
       OCTET          = <any 8-bit sequence of data>
       CHAR           = <any US-ASCII character (octets 0 - 127)>
       UPALPHA        = <any US-ASCII uppercase letter "A".."Z">
       LOALPHA        = <any US-ASCII lowercase letter "a".."z">
       ALPHA          = UPALPHA | LOALPHA
       DIGIT          = <any US-ASCII digit "0".."9">
       CTL            = <any US-ASCII control character
                        (octets 0 - 31) and DEL (127)>
       CR             = <US-ASCII CR, carriage return (13)>
       LF             = <US-ASCII LF, linefeed (10)>
       SP             = <US-ASCII SP, space (32)>
       HT             = <US-ASCII HT, horizontal-tab (9)>
       <">            = <US-ASCII double-quote mark (34)>
"""

def One(chars):
	return Word(chars, max=1)

_chars = ''.join(map(chr, range(128)))
CHAR = One(_chars)
_ctl_chars = ''.join(map(chr, range(0,32))+[chr(127)])
CTL = One(_ctl_chars)
SP = ' '
HT = '\t'

"""
       token          = 1*<any CHAR except CTLs or separators>
       separators     = "(" | ")" | "<" | ">" | "@"
                      | "," | ";" | ":" | "\" | <">
                      | "/" | "[" | "]" | "?" | "="
                      | "{" | "}" | SP | HT
"""

separators = r'()<>@,;:\"/[]?={}' + SP + HT
token = CharsNotIn(_ctl_chars + separators)

"""
       quoted-string  = ( <"> *(qdtext | quoted-pair ) <"> )
       qdtext         = <any TEXT except <">>
       quoted-pair    = "\" CHAR
"""

qdtext = CharsNotIn('"')
quoted_pair = "\\" + CHAR
quoted_string = '"' + ZeroOrMore( qdtext | quoted_pair ) + '"'

"""
	auth-scheme    = token
	auth-param     = token "=" ( token | quoted-string )
"""

auth_scheme = token
auth_param = token + "=" + ( token | quoted_string )

"""
	challenge   = auth-scheme 1*SP 1#auth-param
"""

# need something for n#m(expr) syntax
def ListOfElements(expr, min=0, max=float('Inf')):
	"List of elements separated by commas (and whitespace robust)"
	# todo: implement this

# challenge is auth-scheme followed by one or more spaces followed by
#  one or more auth-params separated by commas.

challenge = auth_scheme + OneOrMore(delimitedList(auth_param))
