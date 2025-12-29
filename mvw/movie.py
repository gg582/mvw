from os import abort
import requests
from pathlib import Path
from omdbapi.movie_search import GetMovie, GetMovieException
from rich.console import Console

from .moai import Moai
from .config import ConfigManager

console = Console()
config_manager = ConfigManager()
moai = Moai()

class MovieManager:
    """Manage any resources and data regarding movies"""
    def __init__(self) -> None:
        self.api_key = config_manager.get_config("API", "omdb_api_key")
        self.omdb = GetMovie(api_key=self.api_key)

    def test_api_key(self, api_key: str) -> bool:
        """Test the validity of the API key"""
        try:
            # Create a new movie instance for testing
            GetMovie(api_key=api_key).get_movie(title='Interstellar')
            return True
        except GetMovieException:
            return False

    def fetch_movie_metadata(self, title: str) -> dict:
        """Fetch movie metadata using OMDB Api Endpoint"""
        try:
            self.movie = self.omdb.get_movie(title=title)
            # print(self.movie.items())
            return self.movie
        except GetMovieException as e:
            moai.says(f"[indian_red]x Sorry, Fetching movie error ({e}) occured.[/]")
            abort()


    def fetch_poster(self):
        """Fetch movie poster and store in posters in data"""
        poster_link = self.movie['poster'] # pyright: ignore
        poster_directory = Path(config_manager.get_config("PATH", "poster_dir"))
        poster_directory.mkdir(parents=True, exist_ok=True)

        filename = poster_link.split("/")[-1].split("@")[0] + ".jpg"
        file_path = poster_directory / filename

        # check if the poster already exist
        if file_path.exists():
            moai.says(f"[yellow]Poster file already exist -> ([italic]No Fetching new one![/])[/]")
            return file_path
        else:
            try:
                response = requests.get(poster_link, stream=True, timeout=10)
                response.raise_for_status() # Check for 404/500 errors

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                moai.says(f"[green]✓ Poster ({file_path}) [italic]saved[/italic] successfully[/]")
                return file_path

            except Exception as e:
                moai.says(f"[indian_red]x Sorry, Poster Error ({e}) occured.[/]")
                return
