
from gi.repository import Notify

if not Notify.init("i3pystatus"):
    raise ImportError("Couldn't initialize libnotify")

URGENCY_LUT = (
    Notify.Urgency.LOW,
    Notify.Urgency.NORMAL,
    Notify.Urgency.CRITICAL,
)

# List of some useful icon names:
# battery, battery-caution, battery-low
# …

def display_notification(title, body, icon="dialog-information", urgency=1, timeout=0):
    notification = Notify.Notification.new(title, body, icon)
    if timeout:
        notification.set_timeout(timeout)
    notification.set_urgency(URGENCY_LUT[urgency])
    return notification.show()

try:
    from PyQt4 import Qt

    app = Qt.QApplication([])

    def display_menu(menu_items, x, y):
        menu = Qt.QMenu()

        for label, callable in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(callable)

        menu.popup(Qt.QPoint(x, y))
        menu.exec_()
except ImportError:
    def display_menu(menu_items, x, y):
        pass
