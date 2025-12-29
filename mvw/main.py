import typer
import click
from iterfzf import iterfzf
from rich.console import Console
from typing import Optional

from .config import ConfigManager
from .display import DisplayManager
from .movie import MovieManager
from .database import DatabaseManager
from .moai import Moai

app = typer.Typer(help="MVW - CLI MoVie revieW")

config_manager = ConfigManager()
movie_manager = MovieManager()
database_manager = DatabaseManager()
moai = Moai()
console = Console()

@app.command()
def config(
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Set OMDb API key"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Set your name as the reviewer"),
    moai_says: Optional[bool] = typer.Option(None, "--moai", "-m", help="Toggle the Moai help", show_default=False),
    poster_width: Optional[str] = typer.Option(None, "--poster-width", "-w", help="Set the poster width (default: 30)"),
    reset: bool = typer.Option(False, "--reset", "-r", help="Reset the config into default configuration"),
):
    """Config Commands"""
    if reset:
        config_manager.reset_to_default_config()

    if api_key:
        # Check the api key validation
        if  movie_manager.test_api_key(api_key):
            config_manager.set_config("API", "omdb_api_key", api_key)
            moai.says(f"[green]✓ API Key [italic]added[/italic] successfully[/]")
        else:
            moai.says(f"[indian_red]x Sorry, API Key ({api_key}) seems [italic]wrong[/]")

    if name:
        config_manager.set_config("USER", "name", name)

    if moai_says:
        moai_bool = config_manager.get_config("UI", "moai").lower() == "true"

        if moai_bool:
            moai.says(f"[dim light_steel_blue3]Bye, see you again later..[/]")
            config_manager.set_config("UI", "moai", "false")
        else:
            config_manager.set_config("UI", "moai", "true")
            moai.says(f"[green]Hi, nice to see you again![/]")

    if poster_width:
        config_manager.set_config("UI", "poster_width", poster_width)
        moai.says(f"[green]✓ Poster width ({poster_width}) [italic]resized[/italic] successfully[/]")


    config_manager.show_config()

@app.command()
def edit(
    movie,
    poster_path: str = "",
    already_reviewed: bool = True
):
    moai.says(
        "The rating can be half [cyan](x.5)[/], it will be shown as [yellow] [/]"
            "[dim]eg:[/] rating 3.5 =>[yellow]     [/][black] [/]"
    )

    if already_reviewed:
        display_manager = DisplayManager(movie, movie['poster_local_path'])
        display_manager.display_movie_info(movie['star'], movie['review'])

        moai.says(
            f"Seems like your past rating is {movie['star']}."
            f"Press [yellow]ENTER[/] if want to skip it"
        )

        star = click.prompt(
            "MVW 󱓥 (0 ~ 5)",
            type=click.FloatRange(0, 5),
            default=movie['star'],
            show_default=True,
            prompt_suffix=">"
        )
        
        moai.says(
            f"Seems like you have already reviewed {movie['title']}, so\n"
            "I recommend for you to [cyan]re-edit[/] using your [italic]default text editor[/]"
            "as you won't need to write them from [indian_red italic]scratch..[/]"
        )

        use_text_editor = click.confirm(
            "MVW 󰭹  text editor",
            default=False,
            prompt_suffix="?",
            show_default=True
        )
        if use_text_editor:
            review: str = click.edit(movie['review']) # pyright: ignore
        else:
            review = click.prompt("MVW 󰭹 ", prompt_suffix=">")

        database_manager.update_star_review(movie['imdbid'], star, review) 
        moai.says(f"[green]✓ Your Star & Review got [italic]updated[/italic] successfully[/]")

        display_manager.display_movie_info(star, review)
    else:
        display_manager = DisplayManager(movie, poster_path)
        display_manager.display_movie_info()
        star = click.prompt(
            "MVW 󱓥 (0 ~ 5)",
            type=click.FloatRange(0, 5),
            default=2.5,
            show_default=True,
            prompt_suffix=">"
        )

        moai.says(
            "The review section [italic]supports[/] [medium_purple1]rich[/] format.\n"
            "You can learn more at [sky_blue2 underline]https://rich.readthedocs.io/en/stable/markup.html[/]\n"
            "[dim]>> Examples: \\[blue]This is blue\\[/blue] -> [blue]This is blue[/blue], + many more[/dim]" # pyright: ignore
            "\n\nIn this section, you can choose to write the review [italic cyan]directly[/] in the terminal [default] (press [yellow]`ENTER`[/])\nor using your [italic hot_pink3]default text editor[/] [yellow](type `y`, `ENTER`)[/]"
        , moai="big")

        use_text_editor = click.confirm(
            "MVW 󰭹  text editor",
            default=False,
            show_default=True,
            prompt_suffix="?"
        )
        if use_text_editor:
            review: str = click.edit() # pyright: ignore
        else:
            moai.says(
                "Be [bold]careful[/] to not make as much mistake as you [indian_red]cannot[/] move to the left except [italic]backspacing[/]"
            )
            review = click.prompt("MVW 󰭹 ", prompt_suffix=">")

        database_manager.store_movie_metadata(movie, poster_path, star, review) 
        display_manager.display_movie_info(star, review)

@app.command()
def search():
    """Search the movie title with OMDb API"""
    if config_manager.get_config("API", "omdb_api_key"):
        # moai.says(
        #     "The title should be the [bold italic indian_red]exact[/]: [yellow]'&'[/] [sky_blue2]vs[/] [yellow]'and'[/], ...\n"
        #     "Also, To exit at [italic]any[/] point, simply [yellow]`CTRL+c`[/]"
        # )
        # title = click.prompt("MVW  ", prompt_suffix=">")
        # movie: dict = movie_manager.fetch_movie_metadata(title=title)
        # poster_path = movie_manager.fetch_poster()
        # poster_path = str(poster_path.resolve())
        
        from mvw.test import TestData
        test_data = TestData()
        movie = test_data.test_movie
        poster_path = test_data.test_poster

        movie_already_reviewed = database_manager.get_movie_metadata_by_title(movie['title'])
        already_reviewed = False

        if movie_already_reviewed:
            movie = movie_already_reviewed
            already_reviewed = True

        edit(movie, poster_path, already_reviewed)
    else:
        moai.says("Hi, [bold]API key[/] [indian_red]did not found[/], try [italic yellow]`mvw config --help`[/]\n"
                    "While doing that, you can apply Free API key here:\n"
                    "       [sky_blue2 underline]http://www.omdbapi.com/apikey.aspx[/]\n"
                    "             [dim]Try CTRL+left_click ^[/]", moai="big")


@app.command()
def list():
    all_reviewed_movies = database_manager.get_all_movies()

    movie_map = {movie['title']: movie for movie in all_reviewed_movies}

    selected_title = iterfzf(
        movie_map.keys(),
        preview="uv run main.py preview {}"
    )

    if selected_title:
        movie_data = movie_map[selected_title]
        print(f"Full details: {movie_data}")

@app.command()
def preview(title: str):
    previewed_movie = database_manager.get_movie_metadata_by_title(title)

    display_manager = DisplayManager(previewed_movie, previewed_movie['poster_local_path'])
    display_manager.display_movie_info(previewed_movie['star'],previewed_movie['review'])


# Default to search
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        search()

if __name__ == "__main__":
    app()
