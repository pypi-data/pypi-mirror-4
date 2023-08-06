import logging
from GUI import GUI
import gtk
logging.basicConfig(level=logging.WARNING)
gui = GUI(2500, 2500, 1, timeout=30)
gtk.main()
