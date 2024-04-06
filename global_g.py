# supports variables that should stay same throughout whole application

import sys

import pint
from PyQt5.QtWidgets import QApplication


global_app = QApplication(sys.argv)

ureg = pint.UnitRegistry()