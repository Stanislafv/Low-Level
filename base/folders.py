import applib
import sys, os

if getattr(sys, 'frozen', False):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(sys.argv[0]))

folder = applib.AppDir(path=path, config=True, tee=True)

mainfolder = folder.mkdir("Assets")
textures = mainfolder.mkdir("Textures")
saves = mainfolder.mkdir("Saves")
music = mainfolder.mkdir("Music")
sounds = mainfolder.mkdir("Sounds")
fonts = mainfolder.mkdir("Fonts")
cursors = mainfolder.mkdir("Cursors")

block_config = mainfolder.read("block_config.json", type="json")
entity_config = mainfolder.read("entity_config.json", type="json")

