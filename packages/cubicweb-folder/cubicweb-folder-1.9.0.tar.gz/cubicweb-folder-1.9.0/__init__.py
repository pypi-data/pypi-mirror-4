"""cubicweb-folder"""

try:
    from cubicweb.web import FACETTES
    FACETTES.add( ('filed_under', 'subject', 'name') )
except ImportError:
    # cubicweb.web not available
    pass
