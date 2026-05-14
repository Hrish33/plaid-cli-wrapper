import importlib
import pkgutil

# Auto-import every module in this package so their @command decorators fire.
# Adding a new command = create a new file here with @command("name"). Nothing else needed.
for _, module_name, _ in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{module_name}")
