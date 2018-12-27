# Artifixer - An image artifact fixing tool
# Copyright (C) 2018 Joran Honig
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
@click.option('-b', help="Blur radius", default=20)
@click.option('-t', help="Blur threshold.", default=10)
@click.option('--input', help="Input image file", required=True)
@click.option('--base', help="Base even image, this is used to find the dust specs and calculate the filter", required=True)
@click.option('--output', help="Name of the output image", required=True)
def newton(e, b, t, input, base, output):
    img = Image.open(base)
    to_fix = Image.open(input)

    avg = Stat(img)._getmedian()
    # e_img = Image.new(img.mode, img.size, (avg[0], avg[1], avg[2], avg[3]))
    e_img = img.filter(BoxBlur(70))
    profile = divide(img, e_img)

    fixed = fix(to_fix, img, profile, e)
    fixed.save(output, "PNG")

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

    blurred = fixed.filter(BoxBlur(b))
    fixed.paste(blurred, None, mr)
    fixed.paste(blurred, None, mg)
    fixed.paste(blurred, None, mb)

    fixed.save("blurred_" + output, "PNG")


if __name__ == "__main__":
    cli()