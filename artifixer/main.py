from PIL import Image
import numpy as np
import click
from PIL.ImageStat import Stat
from sklearn.neural_network import MLPRegressor


def divide(imgA, imgB, e):
    a = np.asarray(imgA)
    b = np.asarray(imgB)

    c = a / b.astype("float")

    return c


def fix(img, base, profile, e):
    a = np.asarray(img)
    b = np.asarray(base)
    factor = 1 + ((b - a) / 256) * e

    modded_profile = profile ** factor
    fixed = a / modded_profile
    return Image.fromarray(fixed.astype('uint8'))


@click.group(help="Image filter utility")
@click.version_option(1)
def cli():
    pass


@cli.command()
@click.option('-e', help="Strength of the filter", default=1.6)
@click.option('--input', help="Input image file", required=True)
@click.option('--base', help="Base image to build profile off", required=True)
@click.option('--output', help="Output image file", required=True)
def newton(e, input, base, output):
    img = Image.open(base)
    to_fix = Image.open(input)

    # img.save("b_input.png", "PNG")
    # to_fix.save("t_input.png", "PNG")

    avg = Stat(img)._getmedian()
    e_img = Image.new(img.mode, img.size, (avg[0], avg[1], avg[2], avg[3]))
    profile = divide(img, e_img, e)

    fixed = fix(to_fix, img, profile, e)
    fixed.save(output, "PNG")



if __name__ == "__main__":
    cli()