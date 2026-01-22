from pathlib import Path
from rich.text import Text
from rich.align import Align

from .base import BaseRenderer
from asciify import asciify
from mvw.config import ConfigManager

poster_width = float(ConfigManager().get_config("UI", "poster_width"))-1
poster_height = int(1.1 * poster_width)

class ASCIIRenderer(BaseRenderer):
    def __rich_console__(self, console, options):
        try:
            if not self.image_path.exists():
                self.failed = True
                return

            result = asciify(
                image_path=str(self.image_path),
                width=int(poster_width),
                height=poster_height,
                edges_detection=True,
            )

            yield Align.center(Text.from_ansi(result))
        except Exception:
            self.failed = True
