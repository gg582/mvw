from pathlib import Path
import configparser
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED

from .moai import Moai

CONFIG_DIR = Path.home() / ".config" / "mvp"
CACHE_DIR = Path.home() / ".cache" / "mvp"

USER_FILE = CONFIG_DIR / "user.conf"
POSTERS_DIR = CACHE_DIR / "posters"

console = Console()
moai = Moai()

class ConfigManager:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.base_dir = Path(__file__).parent.parent
        self.user_file = USER_FILE
        self.load_configs()
        self.save_user_config()

    def load_configs(self):
        """Loads defaults first, then overrides with user settings"""
        # Fallback logic if default.conf is missing from the app folder
        self._set_hardcoded_defaults()

        # Overrides default config
        if self.user_file.exists():
            self.config.read(self.user_file)

    def _set_hardcoded_defaults(self):
        """Fallback if default conf missing"""
        self.config['API'] = {'omdb_api_key': ''}
        self.config['USER'] = {'name': ''}
        self.config['UI'] = {
            'moai': 'true',
            'poster_width': '30',
        }

    def save_user_config(self):
        """Saves only the current state to the user's config file"""
        self.user_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.user_file, 'w') as f:
            self.config.write(f)

    def get_config(self, section:str, key:str, fallback:str = ""):
        """Get the defined settings in the CONFIG_FILE"""
        return self.config.get(section, key, fallback=fallback)

    def reset_to_default_config(self):
        """Reset any changes made in user.conf"""
        preserved_data = self.get_config("API", "omdb_api_key")

        self.config.clear()
        self.load_configs()

        self.set_config("API", "omdb_api_key", preserved_data)
        self.save_user_config()
        moai.says(f"[green]✓ Config [italic]defaulted[/italic] successfully[/]")

    def set_config(self, section: str, key: str, value: str = ""):
        """Update the config object and save it to the user.conf file"""

        # Ensure the section exists before setting a value
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, value)
        self.save_user_config()

    def show_config(self):
        # TODO: Make a table and partition
        """Show the configuration info"""
        table = Table(title="[light_steel_blue3]Configuration Settings[/]", box=ROUNDED)
        table.add_column("Section", style="cyan", width=12)
        table.add_column("Key", style="yellow")
        table.add_column("Value", style="indian_red")

        # Iterate through the sections and keys
        for section in self.config.sections():
            items = self.config.items(section)
            for index, (key, value) in enumerate(items):
                display_section = section if index == 0 else ""
                table.add_row(display_section, key, value if value != "" else "-")
            table.add_section()

        console.print(" ")
        console.print(table)
        console.print(" Try [italic yellow]`config --help`[/] to edit the settings")

if __name__ == "__main__":
    ConfigManager().show_config()
