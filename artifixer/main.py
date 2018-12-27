from PIL import Image
import numpy as np
import click
from PIL.ImageStat import Stat
from PIL.ImageChops import difference
from PIL.ImageFilter import BoxBlur

def divide(imgA, imgB):
    a = np.asarray(imgA)
    b = np.asarray(imgB)
    return a / b.astype("float")


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
@click.option('-b', help="blur radius", default=20)
@click.option('-t', help="blur threshold", default = 10)
@click.option('--input', help="Input image file", required=True)
@click.option('--base', help="Base image to build profile off", required=True)
@click.option('--output', help="Output image file", required=True)
def newton(e, b, t, input, base, output):
    img = Image.open(base)
    to_fix = Image.open(input)

    avg = Stat(img)._getmedian()
    # e_img = Image.new(img.mode, img.size, (avg[0], avg[1], avg[2], avg[3]))
    e_img = img.filter(BoxBlur(70))
    profile = divide(img, e_img)

    fixed = to_fix.copy()
    p_fixed = fix(to_fix, img, profile, e)
    p_fixed.save(output, "PNG")

    R, G, B = 0, 1, 2

    i_split = img.split()

    def rf(p):
        if abs(p - avg[R]) > t:
            return 255
        else:
            return 0

    def gf(p):
        if abs(p - avg[G]) > t:
            return 255
        else:
            return 0

    def bf(p):
        if abs(p - avg[B]) > t:
            return 255
        else:
            return 0
    mr = i_split[R].point(rf)

    mg = i_split[G].point(gf)

    mb = i_split[B].point(bf)

    fixed.paste(p_fixed, None, None)

    blurred = fixed.filter(BoxBlur(b))
    fixed.paste(blurred, None, mr)
    fixed.paste(blurred, None, mg)
    fixed.paste(blurred, None, mb)

    fixed.save("test_" + output, "PNG")


if __name__ == "__main__":
    cli()