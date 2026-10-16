#!/usr/bin/env python3
"""Generate a separate local segmentation mask; never save/rewrite photo pixels."""
import argparse
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from compose import digest, mask_image


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--protect', type=float, nargs=4, required=True,
                   metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'))
    args = p.parse_args()
    if args.out.exists():
        p.error('Output exists; choose a new mask path.')
    if not all(0 <= v <= 1 for v in args.protect):
        p.error('--protect requires normalized bounds')
    l,t,r,b = args.protect
    if l >= r or t >= b:
        p.error('Empty protected region.')
    try:
        from rembg import new_session, remove
    except ImportError:
        p.error('Install rembg[cpu] in a supported local Python environment; see references/framing.md.')
    original = args.image.read_bytes()
    with Image.open(io.BytesIO(original)) as im:
        im = ImageOps.exif_transpose(im).convert('RGB')
    # Fixed local segmentation model, never a cloud/generative background editor.
    mask = remove(im, session=new_session('u2net'), only_mask=True).convert('L')
    if mask.size != im.size:
        raise ValueError('Segmentation returned different dimensions.')
    # Modify only the mask. The face RGB always comes from the original file.
    ImageDraw.Draw(mask).rectangle((int(l*im.width),int(t*im.height),int(r*im.width),int(b*im.height)),fill=255)
    data = io.BytesIO(); mask.save(data, format='PNG')
    mask_image(data.getvalue(), im.size, args.protect)
    if digest(args.image.read_bytes()) != digest(original):
        raise ValueError('Source changed during segmentation.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as f:
        f.write(data.getvalue())
    print('Mask saved separately. Inspect hair, ears, jaw and all facial opacity before composition.')


if __name__ == '__main__':
    main()
