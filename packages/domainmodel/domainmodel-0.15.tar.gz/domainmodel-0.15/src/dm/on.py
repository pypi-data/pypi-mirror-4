try:
    from json import dumps # Needed to avoid mercurial/demandimport.py delaying an error.
    import json
except ImportError:
    import simplejson as json
