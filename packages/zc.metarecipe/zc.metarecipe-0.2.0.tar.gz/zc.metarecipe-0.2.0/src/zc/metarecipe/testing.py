

class Buildout:

    def __init__(self):
        self._raw = {}

    def __getitem__(self, name):
        print "[%s]" % name
        for k, v in sorted(self._raw[name].items()):
            print "%s = %s" % (k, v.replace("\n", "\n  ").strip())
        return self._raw[name]
