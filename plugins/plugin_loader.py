# plugins/plugin_loader.py
import importlib
import os

def load_plugins(plugin_dir="engines"):
    plugins = {}
    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            module = importlib.import_module(f"{plugin_dir}.{module_name}")
            if hasattr(module, "Engine"):
                plugins[module_name] = module.Engine
                print(f"Loaded engine: {plugins[module_name]}")

    return plugins