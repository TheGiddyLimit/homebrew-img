#!/usr/bin/env python3
"""Conversión recursiva y segura a WebP. Requiere Pillow."""
import argparse
from collections import defaultdict
from pathlib import Path
import os
import tempfile

try:
    from PIL import Image, features
except ImportError:
    raise SystemExit('Instalá Pillow: py -m pip install --upgrade Pillow')

EXTS = {'.png', '.jpg', '.jpeg', '.jfif', '.bmp', '.gif', '.tif', '.tiff',
        '.avif', '.ico', '.heic', '.heif', '.jp2', '.j2k', '.ppm', '.pgm', '.pbm', '.tga', '.psd', '.apng', '.pcx', '.dds', '.jxl'}


def convert(source, target, quality):
    temp = None
    try:
        with Image.open(source) as im:
            size = im.size
            count = getattr(im, 'n_frames', 1)
            if count > 1 and im.format not in ('GIF', 'PNG', 'AVIF'):
                raise ValueError('Imagen multipágina: no se convierte para evitar perder páginas')
            if im.mode in ('I', 'I;16', 'I;16B', 'I;16L', 'F'):
                raise ValueError('Profundidad superior a 8 bits: WebP no puede preservarla')
            # Pillow puede reducir algunos PNG RGB de 16 bits a 8 bits al abrirlos.
            if im.format == 'PNG':
                with source.open('rb') as fh:
                    header = fh.read(26)
                if len(header) >= 25 and header[24] == 16:
                    raise ValueError('PNG de 16 bits: WebP no puede preservar su profundidad')
            options = {'format': 'WEBP', 'lossless': quality is None,
                       'quality': 100 if quality is None else quality, 'method': 6, 'exact': True}
            for key in ('icc_profile', 'exif', 'xmp'):
                if im.info.get(key):
                    options[key] = im.info[key]
            frames, durations = [], []
            for i in range(count):
                im.seek(i)
                if im.size != size:
                    raise ValueError('Los fotogramas tienen distintas resoluciones')
                has_alpha = 'A' in im.getbands() or 'transparency' in im.info
                frames.append(im.convert('RGBA' if has_alpha else 'RGB'))
                durations.append(im.info.get('duration', 100))
            if count > 1:
                if im.format == 'PNG' and im.info.get('default_image'):
                    raise ValueError('APNG con imagen de portada independiente: revisión manual')
                options.update(save_all=True, append_images=frames[1:],
                               duration=durations, loop=im.info.get('loop', 0))
            fd, temp_name = tempfile.mkstemp(prefix='.webp_tmp_', suffix='.webp', dir=source.parent)
            os.close(fd)
            temp = Path(temp_name)
            frames[0].save(temp, **options)
            # Leer y decodificar todos los fotogramas antes de tocar el original.
            with Image.open(temp) as check:
                if check.format != 'WEBP' or check.size != size:
                    raise ValueError('El resultado no es WebP o cambió su resolución')
                if getattr(check, 'n_frames', 1) != count:
                    raise ValueError('Cambió la cantidad de fotogramas')
                for i in range(count):
                    check.seek(i)
                    check.load()
        # Exclusión atómica: nunca sobrescribir una imagen ya existente.
        # Crear el destino mediante un enlace duro en el mismo directorio.
        # Si la unidad no lo admite, usar creación exclusiva y copiar.
        try:
            os.link(temp, target)
        except FileExistsError:
            raise
        except OSError:
            import shutil
            with target.open('xb') as out:
                try:
                    with temp.open('rb') as inp:
                        shutil.copyfileobj(inp, out)
                    out.flush()
                    os.fsync(out.fileno())
                except Exception:
                    out.close()
                    target.unlink(missing_ok=True)
                    raise
        # Verificar también el archivo definitivo antes de eliminar el original.
        with Image.open(target) as check:
            if check.format != 'WEBP' or check.size != size or getattr(check, 'n_frames', 1) != count:
                raise ValueError('Falló la verificación del archivo definitivo')
            for i in range(count):
                check.seek(i)
                check.load()
        source.unlink()
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('carpeta', nargs='?', type=Path, default=Path(__file__).resolve().parent,
                        help='Carpeta raíz; por defecto, la carpeta del script')
    parser.add_argument('--apply', action='store_true', help='Convertir y borrar originales. Sin esto, solo muestra el plan.')
    parser.add_argument('--quality', type=int, choices=range(1, 101), metavar='1-100',
                        help='Compresión con pérdida opcional. Por defecto: lossless.')
    args = parser.parse_args()
    root = args.carpeta.expanduser().resolve()
    if not root.is_dir():
        parser.error(f'No existe la carpeta: {root}')
    if not features.check('webp'):
        parser.error('Esta instalación de Pillow no admite WebP.')
    candidates = []
    existing = set()
    skipped_svg = []
    scan_errors = []
    def onerror(error):
        scan_errors.append(str(error))
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
        dirs.sort()
        for name in sorted(files):
            p = Path(directory) / name
            if p.is_symlink() or not p.is_file():
                continue
            existing.add(str(p).casefold())
            if p.suffix.lower() in EXTS and not p.name.startswith('.webp_tmp_'):
                candidates.append(p)
            elif p.suffix.lower() in ('.svg', '.svgz'):
                skipped_svg.append(p)
    groups = defaultdict(list)
    for p in candidates:
        groups[str(p.with_suffix('.webp')).casefold()].append(p)
    planned = converted = failed = conflicts = 0
    print(f'Carpeta: {root}\nModo: {"CONVERTIR Y BORRAR" if args.apply else "SIMULACIÓN (sin cambios)"}\n')
    for source in candidates:
        target = source.with_suffix('.webp')
        key = str(target).casefold()
        if key in existing or len(groups[key]) > 1:
            print(f'[CONFLICTO] {source.relative_to(root)}: nombre de destino repetido; se conserva el original.')
            conflicts += 1
            continue
        planned += 1
        if not args.apply:
            print(f'[PLAN] {source.relative_to(root)} -> {target.name}')
            continue
        try:
            convert(source, target, args.quality)
            converted += 1
            print(f'[OK] {target.relative_to(root)}')
        except Exception as exc:
            failed += 1
            print(f'[ERROR] {source.relative_to(root)}: {exc}')
    for p in skipped_svg:
        print(f'[OMITIDO] {p.relative_to(root)}: SVG vectorial; no tiene resolución raster fija.')
    for e in scan_errors:
        print(f'[ERROR DE ACCESO] {e}')
    print(f'\nDetectadas: {len(candidates)} | Planificadas: {planned} | Convertidas: {converted}')
    print(f'Errores: {failed} | Conflictos: {conflicts} | SVG omitidos: {len(skipped_svg)} | Errores de acceso: {len(scan_errors)}')
    if not args.apply:
        print('Para ejecutar la conversión real, agregá --apply.')
    elif failed or conflicts or skipped_svg or scan_errors:
        print('Quedaron archivos o carpetas pendientes. Revisá los mensajes antes de eliminar nada manualmente.')
    return int(bool(failed or conflicts or scan_errors or skipped_svg))

if __name__ == '__main__':
    raise SystemExit(main())
