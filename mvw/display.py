import re
from typing import Dict
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.columns import Columns
from rich.align import Align
from rich.layout import Layout
from rich_pixels import Pixels
from rich.panel import Panel
from rich import box


from .config import ConfigManager

console = Console(force_terminal=True)
config_manager = ConfigManager()

# NOTE: DATA that we got from OMDB 
# dict_keys(['title', 'year', 'rated', 'released', 'runtime', 'genre', 
# 'director', 'writer', 'actors', 'plot', 'language', 'country', 'awards', 
# 'poster', 'ratings', 'metascore', 'imdbrating', 'imdbvotes', 'imdbid', 
# 'type', 'dvd', 'boxoffice', 'production', 'website'])

class DisplayManager:
    def __init__(self, movie, poster_path) -> None:
        self.movie = movie
        self.poster_path = poster_path
        self.poster_width = int(config_manager.get_config("UI", "poster_width"))
        self.info_width = 100

    def display_movie_info(self, star: float = 0.0, review_text: str = "Your review will show here."):
        """The Movie Review Card"""
        poster_panel = self.poster_panel()
        body_table = Table.grid(padding=(0, 2))

        body_table.add_column(width=self.poster_width) # Space for "Poster"
        body_table.add_column()         # Space for metadata + review

        reviewer_name = config_manager.get_config("USER", "name")

        review_header = Text.from_markup(f"[white bold]󰭹 {reviewer_name.upper() + "'s"} REVIEW :[/] [yellow]{self.iconize_star(float(star))}[/]")
        review = Text.from_markup(review_text, overflow="fold")
        gap = Text.from_markup(" ")

        review_group = Group(
            gap,
            review_header,
            review
        )

        right_group = Group(
            self.movie_group(),
            self.imdb_group(),
            self.stats_group(),
            review_group,
        )

        body_table.add_row(poster_panel, right_group)

        # Combine everything into one main Panel
        main_group = Table.grid(expand=True)
        main_group.add_row(body_table)

        full_panel = Panel(
            main_group,
            box=box.SIMPLE_HEAD,
            width=100
        )
        console.print(full_panel)

    def iconize_star(self, star: float):
        star = max(0, min(5, star))
        full_star = int(star)
        has_half_star = (star - full_star) >= 0.5
        empty_star = 5 - full_star - (1 if has_half_star else 0)

        STAR = " "
        HALF = " "
        EMPTY = "[black] [/]"

        return (STAR * full_star) + (HALF if has_half_star else "") + (EMPTY * empty_star)

    def movie_group(self) -> Group: 
        movie_table = Table.grid(expand=False)
        movie_table.add_column(style="cyan")
        movie_table.add_column(style="white")

        movie_header = Text.from_markup(f"[cyan bold]󰿎 MOVIE : [/]{self.movie['title']} ({self.movie['year']})", style="bold")
        movie_table.add_row("├  : ", str(self.movie['director']))
        movie_table.add_row("├  : ", str(self.movie['language']))
        movie_table.add_row("├  : ", str(self.movie['rated']))
        movie_table.add_row("├ 󰔚 : ", str(self.movie['runtime']))
        movie_table.add_row("├  : ", str(self.movie['released']))
        movie_table.add_row("└ 󰴂 : ", str(self.movie['genre']))

        return Group(
            movie_header,
            movie_table
        )

    def imdb_group(self) -> Group:
        imdb_table = Table.grid(expand=False)
        imdb_table.add_column(style="yellow")
        imdb_table.add_column(style="white", justify="left")

        imdb_header = Text.from_markup(f"[yellow bold]󰈚 IMDB : [/yellow bold]{self.movie['imdbid']}", style="bold")
        imdb_rating = f"{self.movie['imdbrating']}/10 ({self.movie['imdbvotes']})"
        imdb_table.add_row("└  : ", imdb_rating)

        return Group(
            imdb_header,
            imdb_table
        )

    def stats_group(self) -> Group:
        stats_table = Table.grid(expand=False)
        stats_table.add_column(style="red")
        stats_table.add_column(style="white", justify="left")

        stats_header = Text.from_markup(f"[red bold]  STATS : [/red bold]{self.movie['boxoffice']}", style="bold")

        stats: Dict = self.extract_awards(str(self.movie['awards']))

        if stats['oscars'] > 0:
            stats_table.add_row("├ 󰙍 : ", f"Won {stats['oscars']} Oscars")

        stats_table.add_row("├ 󰴥 : ", f"Got {stats['nominations']} Nominations")
        stats_table.add_row("└  : ", f"Won {stats['wins']} Awards")

        return Group(
            stats_header,
            stats_table
        )

    def extract_awards(self, text: str) -> Dict:
        oscar_match = re.search(r'(\d+)\s*Oscar', text, re.IGNORECASE)
        wins_match = re.search(r'(\d+)\s*win', text, re.IGNORECASE)
        nom_match = re.search(r'(\d+)\s*nomination', text, re.IGNORECASE)

        return {
            "oscars": int(oscar_match.group(1)) if oscar_match else 0,
            "wins": int(wins_match.group(1)) if wins_match else 0,
            "nominations": int(nom_match.group(1)) if nom_match else 0
        }

    def poster_panel(self) -> Panel:
        poster_height = int(1.2 * self.poster_width)

        pixels = Pixels.from_image_path(
            path=self.poster_path,
            resize=[self.poster_width, poster_height] # pyright: ignore
        )

        return Panel(
            pixels,
            width=self.poster_width+4,
            height=int((poster_height+5)/2),
            subtitle=str(self.movie['title']),
            expand=True,
        )
    
