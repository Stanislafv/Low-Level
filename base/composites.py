import applib, importlib
from base.folders import folder

composites = {}

for module in applib.Storage("composites").list():
    if not module.endswith(".py"):
        continue
    name = module[:-3]
    mod = importlib.import_module(f"composites.{name}")
    if not hasattr(mod, name):
        folder.log.write(f"The module <composites/{module}> lacks a final class", type=applib.ERROR)
        continue

    composites[name] = getattr(mod, name)