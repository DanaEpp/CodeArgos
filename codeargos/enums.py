from enum import IntEnum

class CodeArgosMode(IntEnum):
    RECON = 0
    REVIEW = 1

class CodeArgosPrintMode(IntEnum):
    NONE = 0
    ID = 1
    DIFF = 2
    BOTH = 3

class CodeDifferMode(IntEnum):
    UNIFIED = 0
    HTML = 1

class WebHookType(IntEnum):
    NONE = 0
    GENERIC = 1
    SLACK = 2
    TEAMS = 3
    DISCORD = 4