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
from PIL.ImageChops import difference, logical_or
from PIL.ImageFilter import BoxBlur, GaussianBlur, BLUR, MaxFilter

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
@click.option('-t', help="Strategy threshold.", default=20)
@click.option('--input', help="Input image file", required=True)
@click.option('--base', help="Base even image, this is used to find the dust specs and calculate the filter", required=True)
@click.option('--output', help="Name of the output image", required=True)
def newton(e, b, t, input, base, output):
    blanc = Image.open(base)
    to_fix = Image.open(input)

    # Apply blanc image fix strategy
    expected_img = blanc.filter(BoxBlur(90))
    profile = divide(blanc, expected_img)

    first_pass = fix(to_fix, blanc, profile, e)
    first_pass.save(output + ".without_blur", "PNG")

    # Create mask
    R, G, B = 0, 1, 2
    avg = Stat(blanc)._getmedian()

    d = Image.fromarray(np.abs(np.asarray(blanc) / np.asarray(expected_img).astype("float") * 100).astype("uint8"))
    i_split = d.split()

    def tr(p):
        if p < t:
            return 255
        else:
            return 0

    m = i_split[G].point(tr)
    mr = i_split[R].point(tr)
    mb = i_split[B].point(tr)

    m = m.filter(MaxFilter(5))
    mr = mr.filter(MaxFilter(5))
    mb = mb.filter(MaxFilter(5))

    m.save("diff.png", "PNG")

    # Apply box blur strategy
    second_pass = first_pass.filter(BoxBlur(b))

    # Put the results in the original image
    to_fix.paste(second_pass, None, m)
    to_fix.paste(second_pass, None, mr)
    to_fix.paste(second_pass, None, mb)

    # save
    to_fix.save(output, "PNG")


if __name__ == "__main__":
    cli()