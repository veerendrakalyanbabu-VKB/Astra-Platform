import importlib.util

from pathlib import Path

from typing import List





class PluginManager:

    """

    Discovers and loads Astra plugins from the plugins/ directory.

    """



    def __init__(self, plugins_dir: Path = None):

        self.plugins_dir = plugins_dir or Path("plugins")

        self.loaded_plugins: List[str] = []



    def load_all(self, core) -> int:

        if not self.plugins_dir.exists():

            self.plugins_dir.mkdir(parents=True, exist_ok=True)

            return 0



        count = 0



        for plugin_file in sorted(self.plugins_dir.glob("*.py")):

            if plugin_file.name.startswith("_"):

                continue



            if self.load_one(plugin_file, core):

                count += 1



        return count



    def load_one(self, plugin_file: Path, core) -> bool:

        if plugin_file.stem in self.loaded_plugins:

            return True



        return self._load_plugin(plugin_file, core)



    def _load_plugin(self, plugin_file: Path, core) -> bool:

        module_name = f"astra_plugin_{plugin_file.stem}"



        spec = importlib.util.spec_from_file_location(module_name, plugin_file)

        module = importlib.util.module_from_spec(spec)



        try:

            spec.loader.exec_module(module)

        except Exception as error:

            if core.logger:

                core.logger.error(f"Plugin load failed ({plugin_file.name}): {error}")

            return False



        register = getattr(module, "register", None)



        if not callable(register):

            if core.logger:

                core.logger.warn(f"Plugin skipped ({plugin_file.name}): no register() function")

            return False



        try:

            register(core)

            self.loaded_plugins.append(plugin_file.stem)



            if core.logger:

                core.logger.info(f"Plugin loaded: {plugin_file.stem}")



            return True



        except Exception as error:

            if core.logger:

                core.logger.error(f"Plugin register failed ({plugin_file.name}): {error}")

            return False

