from haystack_queryparser import ParseSQ
from haystack_queryparser import NoMatchingBracketsFound
from haystack_queryparser import UnhandledException

or_parser = ParseSQ('OR')
and_parser = ParseSQ('AND')