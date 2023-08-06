__author__ = 'palli'


from pynag.Plugins import new_threshold_syntax

print new_threshold_syntax.check_threshold(-23, ok="0..10", warning="10..20")