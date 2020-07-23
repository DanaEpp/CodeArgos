from enum import IntEnum

class CodeArgosMode(IntEnum):
    RECON = 0
    REVIEW = 1

class CodeArgosPrintMode(IntEnum):
    NONE = 0
    ID = 1
    DIFF = 2
    BOTH = 3
