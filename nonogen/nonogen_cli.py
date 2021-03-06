from generator import no_generator
import click
import sys
import re


@click.command()
@click.option("--img",
              prompt="Where is the source image located?",
              help="Image source as path/to/img .jpg and .png only.",
              type=click.Path(exists=True))
@click.option("--size",
              nargs=1,
              prompt="What size nonogram do you want to generate?",
              help="Size of the nonogram to be generated as WIDTHxHEIGHT | example: 16x16",
              type=str)
@click.option("--colour/--black-white",
              help="Type of nonogram. Default black and white.",
              default=False)
def nonogen(img, size, colour):
    """
    Handles cli using click
     calls main class for nonogram generation
    :param img: image path | str
    :param size: size of nonogram | str
    :param colour: type of nonogram | bool
    """
    if not re.search(r"\.(jpg|png)", img):
        click.echo("Only .png and .jpg files are accepted.")
        sys.exit()

    no_generator(img_path=img, size=size, colour=colour).run()


if __name__ == "__main__":
    nonogen()
