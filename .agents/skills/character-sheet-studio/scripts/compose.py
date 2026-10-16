#!/usr/bin/env python3
"""Local, deterministic composition. Requires Python 3 and Pillow."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageOps

ROLES = ('front', 'body', 'profile')
MIMES = {'JPEG': 'image/jpeg', 'PNG': 'image/png', 'WEBP': 'image/webp'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect(data):
    with Image.open(io.BytesIO(data)) as im:
        if im.format not in MIMES or getattr(im, 'n_frames', 1) != 1:
            raise ValueError('Use a static JPEG, PNG or WebP source.')
        mime = MIMES[im.format]
        # Honor display orientation; originals are never rewritten.
        displayed = ImageOps.exif_transpose(im).convert('RGBA')
        return mime, displayed


def layout(blobs, width, framing):
    height = width * 3 // 8
    widths = (width * 29 // 100, width * 39 // 100, width * 32 // 100)
    placements, x = {}, 0
    for role, zone_width in zip(ROLES, widths):
        _, im = inspect(blobs[role])
        if role == 'body':
            scale = min(zone_width / im.width, height / im.height)
            dx = (zone_width - round(im.width * scale)) // 2
            dy = (height - round(im.height * scale)) // 2
            bounds = None
        else:
            # Explicit visual annotation: complete hair/head through chin.
            bounds = framing.get(role, {}).get('head_box')
            if not isinstance(bounds, list) or len(bounds) != 4:
                raise ValueError(f'{role}: provide normalized head_box [left, top, right, bottom].')
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in bounds):
                raise ValueError(f'{role}: head_box coordinates must be finite numbers in [0, 1].')
            left, top, right, bottom = bounds
            if left >= right or top >= bottom:
                raise ValueError(f'{role}: empty head_box.')
            head_w = (right-left) * im.width
            head_h = (bottom-top) * im.height
            scale = min(height * .74 / head_h, zone_width * .94 / head_w)
            if head_h * scale < height * .65:
                raise ValueError(f'{role}: head too wide for a large close-up in this zone; review annotation/layout.')
            dx = round(zone_width / 2 - (left+right) * im.width * scale / 2)
            dy = round(height * .04 - top * im.height * scale)
        size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
        placements[role] = {'zone': [x, 0, zone_width, height],
                            'display_source_size': list(im.size),
                            'scale': scale, 'raster_size': list(size),
                            'position': [x + dx, dy],
                            'head_box': bounds,
                            'fit': 'contain' if role == 'body' else 'reversible_head_viewport'}
        x += zone_width
    return placements


def mask_image(data, size, face_box):
    with Image.open(io.BytesIO(data)) as m:
        if m.format != 'PNG' or m.mode != 'L' or m.size != size:
            raise ValueError('Masks must be grayscale PNG at EXIF-oriented original dimensions.')
        mask = m.copy()
    if not isinstance(face_box, list) or len(face_box) != 4:
        raise ValueError('Cutouts require normalized protected_face_box inside the visible face.')
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in face_box):
        raise ValueError('Invalid protected_face_box.')
    l, t, r, b = face_box
    if l >= r or t >= b:
        raise ValueError('Empty protected face region.')
    box = (int(l*size[0]), int(t*size[1]), int(r*size[0]), int(b*size[1]))
    if box[0] >= box[2] or box[1] >= box[3] or mask.crop(box).getextrema() != (255, 255):
        raise ValueError('Mask alters protected facial pixels; correct the mask, never the photo.')
    if mask.getextrema()[0] == 255:
        raise ValueError('Mask removes no background.')
    return mask


def render(blobs, width, framing, masks):
    height = width * 3 // 8
    canvas = Image.new('RGB', (width, height), '#808080')
    placements = layout(blobs, width, framing)
    for role in ROLES:
        _, im = inspect(blobs[role])
        p = placements[role]
        if role in masks:
            im.putalpha(mask_image(masks[role], im.size, framing[role].get('protected_face_box')))
        x, _, zone_width, _ = p['zone']
        # Clip only the rendered viewport. Retain the entire encoded source.
        panel = Image.new('RGB', (zone_width, height), '#808080')
        resized = im.resize(tuple(p['raster_size']), Image.Resampling.LANCZOS)
        panel.paste(resized, (p['position'][0]-x, p['position'][1]), resized)
        canvas.paste(panel, (x, 0))
    return canvas, placements


def master(blobs, width, framing, masks):
    placements = layout(blobs, width, framing)
    items = []
    for role in ROLES:
        mime, _ = inspect(blobs[role])
        uri = 'data:' + mime + ';base64,' + base64.b64encode(blobs[role]).decode('ascii')
        p = placements[role]
        x, _, zone_width, height = p['zone']
        iw, ih = p['raster_size']
        dx, dy = p['position'][0]-x, p['position'][1]
        style = (f'width:{100*iw/zone_width:.10f}%;height:{100*ih/height:.10f}%;'
                 f'left:{100*dx/zone_width:.10f}%;top:{100*dy/height:.10f}%;')
        if role in masks:
            mask_uri = 'data:image/png;base64,' + base64.b64encode(masks[role]).decode('ascii')
            style += f'mask-image:url({mask_uri});mask-mode:luminance;mask-size:100% 100%;'
        items.append(f'<div style="width:{100*zone_width/width}%"><img alt="{role}" style="{style}" src="{uri}"></div>')
    return ('<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
            '<title>Character sheet</title><style>'
            'html,body{margin:0;background:#808080}main{display:flex;'
            f'width:min({width}px,100vw);height:min({width * 3 // 8}px,37.5vw);background:#808080}}'
            'main>div{position:relative;height:100%;min-width:0;overflow:hidden}'
            'img{position:absolute;display:block;max-width:none;image-orientation:from-image}'
            '</style><main>' + ''.join(items) + '</main></html>')


def verify(out):
    report = json.loads((out / 'integrity.json').read_text())
    width = report['width']
    if report.get('version') != 2:
        raise ValueError('This verifier requires a version 2 composition.')
    framing = report['framing']
    masks = {}
    for role, entry in report.get('masks', {}).items():
        if role not in ('front', 'profile'):
            raise ValueError('Invalid mask role.')
        path = (out / entry['file']).resolve()
        if not path.is_relative_to((out / 'masks').resolve()):
            raise ValueError('Mask path outside masks directory.')
        masks[role] = path.read_bytes()
        if digest(masks[role]) != entry['sha256']:
            raise ValueError('Mask integrity mismatch.')
    if report['background_mode'] == 'cutout' and set(masks) != {'front', 'profile'}:
        raise ValueError('Missing portrait mask.')
    if width < 800 or width % 800:
        raise ValueError('Invalid width.')
    blobs = {}
    for role in ROLES:
        entry = report['sources'][role]
        path = (out / entry['file']).resolve()
        if not path.is_relative_to((out / 'originals').resolve()):
            raise ValueError('Source path outside originals directory.')
        blobs[role] = path.read_bytes()
        if digest(blobs[role]) != entry['sha256']:
            raise ValueError(f'Original hash mismatch: {role}')
    expected_html = master(blobs, width, framing, masks).encode()
    if (out / 'board.html').read_bytes() != expected_html:
        raise ValueError('Master changed or embedded originals differ.')
    expected, placements = render(blobs, width, framing, masks)
    if placements != report['placements']:
        raise ValueError('Placement manifest mismatch.')
    with Image.open(out / 'board.png') as actual:
        if actual.mode != 'RGB' or actual.size != expected.size or actual.tobytes() != expected.tobytes():
            raise ValueError('PNG does not match permitted composition.')
    for filename, sha in report['outputs'].items():
        if filename not in ('board.html', 'board.png') or digest((out / filename).read_bytes()) != sha:
            raise ValueError('Output hash mismatch.')
    print('PASS: original hashes, embedded bytes, placements and raster composition verified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for role in ROLES:
        parser.add_argument('--' + role, type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--background', choices=('cutout', 'original'), default='cutout')
    parser.add_argument('--front-mask', type=Path)
    parser.add_argument('--profile-mask', type=Path)
    parser.add_argument('--framing', type=Path, help='Required JSON: front/profile normalized head_box annotations')
    parser.add_argument('--width', type=int, default=4800)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if args.verify:
        verify(args.verify.resolve())
        return
    if not args.out or not args.framing or not all(getattr(args, r) for r in ROLES):
        parser.error('--front, --profile, --body, --framing and --out are required. Whole-photo fallback is disabled.')
    if args.width < 800 or args.width % 800:
        parser.error('--width must be a positive multiple of 800, at least 800.')
    # Preflight all inputs before creating anything. Refuse existing output dirs.
    blobs = {r: getattr(args, r).read_bytes() for r in ROLES}
    for data in blobs.values():
        inspect(data)
    if blobs['front'] == blobs['profile']:
        parser.error('Front and profile must be distinct photos.')
    framing = json.loads(args.framing.read_text())
    if not isinstance(framing, dict):
        parser.error('--framing must be a JSON object.')
    masks = {}
    if args.background == 'cutout':
        if not args.front_mask or not args.profile_mask:
            parser.error('Cutout mode requires --front-mask and --profile-mask. Never substitute whole photos silently.')
        masks = {r: getattr(args, r + '_mask').read_bytes() for r in ('front', 'profile')}
    elif args.front_mask or args.profile_mask:
        parser.error('Mask inputs conflict with original-background mode.')
    canvas, placements = render(blobs, args.width, framing, masks)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'originals').mkdir()
    sources = {}
    for role in ROLES:
        mime, _ = inspect(blobs[role])
        suffix = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp'}[mime]
        relative = 'originals/' + role + suffix
        (out / relative).write_bytes(blobs[role])
        if getattr(args, role).read_bytes() != blobs[role]:
            raise ValueError('Source changed during composition; do not deliver.')
        sources[role] = {'file': relative, 'sha256': digest(blobs[role]), 'mime': mime,
                         'provenance': 'generated_body_panel' if role == 'body' else 'user_original'}
    mask_report = {}
    if masks:
        (out / 'masks').mkdir()
        for role, data in masks.items():
            path = 'masks/' + role + '.png'
            (out / path).write_bytes(data)
            mask_report[role] = {'file': path, 'sha256': digest(data)}
    (out / 'board.html').write_text(master(blobs, args.width, framing, masks), encoding='utf-8')
    canvas.save(out / 'board.png')
    report = {'version': 2, 'framing': framing, 'masks': mask_report, 'background_mode': args.background, 'width': args.width, 'height': args.width * 3 // 8,
              'background': '#808080', 'sources': sources, 'placements': placements,
              'outputs': {f: digest((out / f).read_bytes()) for f in ('board.html', 'board.png')},
              'limits': 'Hashes establish received-file integrity, not photographic authenticity. '
                        'PNG uses proportional resampling and EXIF display orientation. '
                        'HTML rendering and color management may vary by browser. '
                        'Semantic and visual review required. Keep initial source hashes separately.'}
    (out / 'integrity.json').write_text(json.dumps(report, indent=2) + '\n')
    verify(out)


if __name__ == '__main__':
    main()
