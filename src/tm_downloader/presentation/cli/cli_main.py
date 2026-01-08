import click


@click.command()
@click.option('--url', '-u', help="The url to download", required=True, type=str, show_default=False)
@click.option('--url_range', '-r', help="The range of urls to download", required=True, type=str, show_default=False)
def initializer_cli() -> None:
    pass