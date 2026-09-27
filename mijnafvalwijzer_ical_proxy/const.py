from enum import Enum
import re

MONTHS = {
    "januari":   1,
    "februari":  2,
    "maart":     3,
    "april":     4,
    "mei":       5,
    "juni":      6,
    "juli":      7,
    "augustus":  8,
    "september": 9,
    "oktober":   10,
    "november":  11,
    "december":  12,
}

DATE_RE = re.compile(r"^(\w+) (\d+) (\w+)$")


class WasteType(str, Enum):
    GFT = "gft"
    RESTAFVAL = "restafval"
    PAPIER = "papier"
    PMD = "pmd"
    PLASTIC = "plastic"
    GLAS = "glas"
    TEXTIEL = "textiel"
    GROFVUIL = "grofvuil"
    KERSTBOMEN = "kerstbomen"
