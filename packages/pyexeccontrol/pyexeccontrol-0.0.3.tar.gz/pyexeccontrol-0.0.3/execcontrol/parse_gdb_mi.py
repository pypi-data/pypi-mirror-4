from pyparsing import *

def delimList(rule, delim=","):
    return rule + ZeroOrMore(Suppress(Literal(delim)) + rule) | Empty ()

def props_to_dict(s,l,ts):
    dict = {}
    for t in ts:
        dict[t[0]]=t[1]
    return dict

prefix = Word ("^=*", exact = 1)
id = Word (alphas+"_-")
topic = id
event = Group(prefix + topic)
name = id
object = Forward()
array = Suppress("[") + Group(delimList (object)) + Suppress("]")
string = dblQuotedString.setParseAction(removeQuotes)
value = string | array | object
property = Group(name + Suppress("=") + value)
props = (delimList (property))
object << Suppress("{") + props.setParseAction(props_to_dict) + Suppress("}")
infoline = event + Suppress(",") + props
