import pystray
from PIL import Image
from pystray import MenuItem as item

icon_image = Image.open("../resources/spo.png")


def action():
    print('hey')


menu = (item('name', action), item('name', action))
icon = pystray.Icon("name", icon_image, "title", menu)
icon.run()