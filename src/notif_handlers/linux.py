import notify2


def linux_notify(title, text, icon_path, duration):

    notify2.init('')

    n = notify2.Notification(title, text, icon=icon_path)

    n.set_timeout(duration)
    n.show()