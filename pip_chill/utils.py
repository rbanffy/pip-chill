# #!/usr/local/bin/python
# # -*- coding: utf-8 -*-


class Distribution:
    def __init__(self, name, version=None, required_by=None):
        self.name = name
        self.version = version
        self.required_by = set(required_by) if required_by else set()

    def get_name_without_version(self):
        if self.required_by:
            return '# {} # Installed as dependency for {}' \
                .format(self.name, ', '.join(self.required_by))
        return self.name

    def __str__(self):
        if self.required_by:
            return '# {}=={} # Installed as dependency for {}' \
                .format(self.name, self.version, ', '.join(self.required_by))
        return '{}=={}'.format(self.name, self.version)

    def __cmp__(self, other):
        if isinstance(other, Distribution):
            return self.name == other.name

        return self.name == other

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return self.name
