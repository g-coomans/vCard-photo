import base64
import hashlib
import urllib.request
from urllib.error import HTTPError, URLError
import random
import colorsys
import math

import cairosvg
import cv2
import vobject

DICEBEAR_SPRITES = {
    "adventurer": True,
    "adventurer-neutral": False,
    "avataaars": True,
    "big-ears": True,
    "big-ears-neutral": False,
    "big-smile": True,
    "bottts": False,
    "croodles": False,
    "croodles-neutral": False,
    "identicon": False,
    "initials": False,
    "micah": True,
    "miniavs": False,
    "open-peeps": False,
    "personas": True,
    "pixel-art": False,
    "pixel-art-neutral": False,
}

H_RANGE = (0, 360)
S_RANGE = (50, 75)
L_RANGE = (25, 60)


def retrieveAvatar(seed: str, sprites: str, output: str = "avatar.svg") -> bool:
    """
    Retrieve a avatar with a color background from https://avatars.dicebear.com
    and save it in your currend folder
    Background is based on idea from :
        https://dev.to/admitkard/auto-generate-avatar-colors-randomly-138j
    Input :
        seed : a string hash to produce the avatar
        sprites : determine which sort of avatar you want
        (see https://avatars.dicebear.com)
    Output : SVG file
    Return the file name in case of success
    """
    try:
        background = "%23" + "".join(f"{i:02x}" for i in generateRGB(seed)).upper()
        seed = hashlib.md5(seed).hexdigest()
        urllib.request.urlretrieve(
            f"https://avatars.dicebear.com/api/{sprites}/:{seed}.svg?background={background}",
            output,
        )
        return output
    except HTTPError as err:
        print(err.status, err.reason)
        return False
    except URLError as err:
        print(err.reason)
        return False
    except TimeoutError:
        print("Request timed out")
        return False


def generateIntHashFromStr(s: str) -> int:
    """Generate a int from a string
    First, the string is hashed with md5 method (base hexadecimal).
    Secondly, the hash is converted in int (base decimal).
    To end, it return the 3 last number of this.
    """
    hexadecimalHash = hashlib.md5(s).hexdigest()
    decimalHash = int(hexadecimalHash, 16)
    return decimalHash % (10**3)


def normalizeHash(hash: int, range: tuple) -> int:
    """Normalize a hash in the given range"""
    return math.floor((hash % (range[1] - range[0])) + range[0])


def generateHSL(seed: str) -> tuple:
    """ """
    hash = generateIntHashFromStr(seed)
    h = normalizeHash(hash, H_RANGE) / 360
    s = normalizeHash(hash, S_RANGE) / 100
    l = normalizeHash(hash, L_RANGE) / 100

    return (h, s, l)


def generateRGB(seed: str) -> tuple:
    """Return a RGB tuple from a string"""
    HSL = generateHSL(seed)
    RGB = colorsys.hls_to_rgb(HSL[0], HSL[1], HSL[2])
    return tuple(int(i * 255) for i in RGB)


def svg2pngResized(infile: str, outfile: str = "avatar_resized.png") -> bool:
    """
    Convert a SVG file to a 200x200 px PNG file
    Input : SVG file ended with 'svg'
    Ouput : PNG file with size of 200 px
    Return True in case of success
    """
    if infile.endswith("svg"):
        cairosvg.svg2png(url=infile, write_to=outfile)
        img = cv2.imread(outfile)
        resizeImg = cv2.resize(img, (200, 200))
        cv2.imwrite(outfile, resizeImg)
        return outfile
    else:
        raise ValueError("infile is not a SVG-file.")
        return False


def getSprites() -> list:
    """Get a list of all accepted Sprites by user
    in DICEBEAR_SPRITES"""
    keys_iter = filter(lambda k: DICEBEAR_SPRITES[k] is True,
                       DICEBEAR_SPRITES.keys())
    keys_list = list(keys_iter)

    return keys_list


def b64Image(filename: str) -> str:
    """Return a base64 str of a file"""
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read())
    return b64.decode("UTF-8")


def createImage(seed: str, sprite: str) -> str:
    avatarSvg = retrieveAvatar(seed, sprite)
    avatarPng = svg2pngResized(avatarSvg)

    return b64Image(avatarPng)


def getExistingB64Image(photoValue: str) -> str:
    """Extract a Base64 Image from photo value of VCF V4.0"""
    return photoValue.split("base64,")[1]


def getExistingFormatImage(photoValue: str) -> str:
    """Extract a image format from photo value of VCF V4.0"""
    return photoValue.split("image/")[1].split(";")[0]


def addPhoto(infile: str, outfile: str = None) -> bool:
    """ Add a avatar with a color background at all vCard
    existing in 'infile' and save it in 'outfile'
    
    ATTENTION : all vCard will be saved in Version 3.0
    The conversion is not completly just.
    
    """
    if outfile is None:
        if infile.endswith(".vcf"):
            outfile = infile.split(".vcf")[0] + "_photos.vcf"
        else:
            outfile = infile + "_photos.vcf"
    with open(infile) as f:
        indata = f.read()
        vc = vobject.readComponents(indata)
        vo = next(vc, None)
        while vo is not None:
            if not hasattr(vo, "photo"):
                seed = vo.fn.value.encode("utf-8")

                o = vo.add("PHOTO;ENCODING=b;TYPE=png")
                o.value = createImage(seed, random.choice(getSprites()))
                vo.version.value = "3.0"

            else:
                if vo.version.value == "4.0":
                    # Delete the version 4.0
                    # and create a new entry with version 3.0
                    initial_value = vo.photo.value
                    del vo.photo

                    o = vo.add(
                        "PHOTO;ENCODING=b;TYPE="
                        + getExistingFormatImage(initial_value)
                    )
                    o.value = getExistingB64Image(initial_value)
                    vo.version.value = "3.0"
                elif vo.version.value == "3.0":
                    # In this case, the contact has a photo at version 3.0
                    # So we directly can write this contact.
                    pass

            with open(outfile, "a+") as writer:
                writer.write(vo.serialize())
                writer.write("\n")
            vo = next(vc, None)

if __name__ == "__main__":
    addPhoto("contact.vcf")
