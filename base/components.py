import applib, importlib
from base.folders import folder

components = {}

for module in applib.Storage("components").list():
    if not module.endswith(".py"):
        continue
    name = module[:-3]
    mod = importlib.import_module(f"components.{name}")
    if not hasattr(mod, name):
        folder.log.write(f"The module <components/{module}> lacks a final class", type=applib.ERROR)
        continue

    components[name] = getattr(mod, name)