#!/usr/bin/env python3
"""Build the guard's Printables files and local listing preview."""
from concurrent.futures import ThreadPoolExecutor
from html import escape
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import subprocess

import numpy as np
import trimesh
import pymupdf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MARKETING = HERE / "marketing"
SOURCE = HERE / "n0sa_rlp_v3_guard.scad"
PHOTO = HERE / "images/rlp-v3-key.jpg"
OUTPUT = ROOT / "output/printables/n0sa-rlp-v3-guard"
PARTS = {
    "guard": ([41.67, 33.07, 41.47], "The complete cover. Print one, nose-down, at 0.20 mm layers; supports off."),
}
VIEWS = {
    "hero": ("65,-85,70,0,3,13", "The guard's open rear, magnet pockets and stops. CAD render."),
    "nose": ("65,90,55,0,8,12", "Closed nose and tapered sides. CAD render."),
    "print_orientation": ("70,-90,75,0,17,20", "Print with the closed nose on the plate and opening upward. CAD render."),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def openscad(output, source, definitions=(), image_camera=None):
    command = ["openscad", "--backend=Manifold", "--hardwarnings"]
    if image_camera:
        command += ["--render", "--imgsize=1600,1200", "--projection=ortho",
                    f"--camera={image_camera}", "--viewall", "--autocenter",
                    "--colorscheme=Tomorrow"]
    else:
        command += ["--export-format=binstl"]
    for definition in definitions:
        command += ["-D", definition]
    completed = subprocess.run(command + ["-o", str(output), str(source)],
                               capture_output=True, text=True)
    require(completed.returncode == 0 and output.is_file() and
            "WARNING:" not in completed.stderr and "ERROR:" not in completed.stderr,
            f"OpenSCAD failed for {output.name}:\n{completed.stderr}")


def export_mesh(part):
    name = f"rlp_v3_{part}.stl"
    output = OUTPUT / name
    definitions = [f'part="{part}"']
    openscad(output, SOURCE, definitions)
    mesh = trimesh.load_mesh(output)
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
            f"Invalid mesh: {name}")
    require(len(mesh.split(only_watertight=False)) == 1, f"Disconnected mesh: {name}")
    size, description = PARTS[part]
    require(np.allclose(mesh.extents, size, atol=0.001) and
            abs(mesh.bounds[0, 2]) < 0.001, f"Unexpected dimensions/bed position: {name}")
    return {"file": name, "description": description, "definitions": definitions,
            "size_mm": mesh.extents.tolist(), "watertight": True}


def magnet_diagram():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">
<rect width="1400" height="760" fill="#f7f7f5"/>
<g font-family="Arial, sans-serif" fill="#252b31">
<text x="75" y="90" font-size="42" font-weight="700">A flat magnet seat, with a little room for glue</text>
<text x="75" y="140" font-size="26">Two 6 mm disc magnets per guard · check polarity before inserting</text>
<path d="M100 220H202V456H350V464H550V456H698V220H800V560H100Z" fill="#c75929"/>
<rect x="210" y="219.2" width="480" height="236.8" fill="#aab2bd"/>
<rect x="350" y="456" width="200" height="8" fill="#2f7792"/>
<text x="450" y="335" text-anchor="middle" font-size="32" font-weight="700">6 × ~3 mm magnet</text>
<text x="450" y="380" text-anchor="middle" font-size="25">Fit reference: 2.96 mm thick</text>
<g transform="translate(850,250)" font-size="26">
<text y="0">Pocket: Ø6.20 mm</text>
<text y="55">Seat: 2.95 mm deep</text>
<text y="110">Glue recess: Ø2.50 × 0.10 mm</text>
<text y="165">Bottom: 4.25 mm</text>
<text y="220">Backing below recess: 1.20 mm</text>
</g>
<text x="75" y="645" font-size="25">The surrounding flat ring sets the seat. Use a tiny amount of glue in the center recess.</text>
<text x="75" y="700" font-size="23" fill="#606973">Cross-section through one pocket. Diagram only; measure your magnets before installing.</text>
</g></svg>'''


def write_zip(path, payloads):
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name, data in payloads.items():
            archive.writestr(name, data)
        archive.writestr("SHA256.json", json.dumps(hashes, indent=2) + "\n")
    with ZipFile(path) as archive:
        require(archive.testzip() is None, f"ZIP CRC error: {path.name}")
        for name, digest in hashes.items():
            require(hashlib.sha256(archive.read(name)).hexdigest() == digest, name)


def main():
    inputs = [SOURCE, HERE / "README.md", PHOTO, Path(__file__).resolve(),
              *sorted(MARKETING.iterdir())]
    input_hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in inputs if path.is_file()}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for obsolete in ("rlp_v3_height_coupon.stl", "rlp_v3_floor_coupon.stl",
                     "rlp_v3_depth_gauge.stl", "height_coupon.png",
                     "README.md", "print-and-fit.txt"):
        (OUTPUT / obsolete).unlink(missing_ok=True)
    metadata = json.loads((MARKETING / "metadata.json").read_text())
    require(len(metadata["summary"]) <= 120, "Printables summaries are limited to 120 characters")
    with ThreadPoolExecutor(max_workers=3) as pool:
        meshes = list(pool.map(export_mesh, PARTS))
    for view, (camera, _) in VIEWS.items():
        openscad(OUTPUT / f"{view}.png", MARKETING / "views.scad",
                 [f'view="{view}"'], camera)
    (OUTPUT / "magnet-pocket.svg").write_text(magnet_diagram())
    with pymupdf.open(OUTPUT / "magnet-pocket.svg") as vector:
        with pymupdf.open(stream=vector.convert_to_pdf(), filetype="pdf") as drawing:
            scale = 1600 / drawing[0].rect.width
            drawing[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale)).save(
                OUTPUT / "magnet-pocket.png")
    description = (MARKETING / "printables.html").read_text()
    (OUTPUT / "description.html").write_text(description)
    (OUTPUT / SOURCE.name).write_bytes(SOURCE.read_bytes())
    (OUTPUT / "images").mkdir(exist_ok=True)
    (OUTPUT / "images/rlp-v3-key.jpg").write_bytes(PHOTO.read_bytes())
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    (OUTPUT / "file-descriptions.txt").write_text("\n\n".join(
        f"{entry['file']}\n{entry['description']}" for entry in meshes) +
        f"\n\n{SOURCE.name}\nEditable OpenSCAD source.\n")
    figures = {view: f'<figure><img src="{view}.png" alt="{escape(caption)}">'
               f'<figcaption>{escape(caption)}</figcaption></figure>'
               for view, (_, caption) in VIEWS.items()}
    preview = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(metadata['title'])} — listing preview</title>
<style>body{{font:17px/1.65 system-ui,sans-serif;color:#252b31;background:#f7f7f5;margin:0}}
main{{max-width:1040px;margin:auto;padding:36px 28px}}h1{{font-size:38px;line-height:1.15}}
h3{{margin-top:2em}}a{{color:#99411e}}.status{{font-size:14px;color:#666}}
.summary{{font-size:21px;max-width:850px}}table{{border-collapse:collapse;width:100%;font-size:15px}}
th,td{{border:1px solid #d2d5d7;padding:10px;text-align:left}}figure{{margin:24px 0}}
img{{display:block;width:100%;height:auto}}figcaption{{color:#5b626b;font-size:14px;margin-top:8px}}
.gallery{{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}}.gallery figure{{margin:0}}
.download{{display:inline-block;background:#99411e;color:white;padding:8px 16px;border-radius:5px;text-decoration:none}}
@media(max-width:700px){{.gallery{{display:block}}.gallery figure{{margin:20px 0}}main{{padding:24px 16px}}h1{{font-size:30px}}table{{font-size:12px;overflow-wrap:anywhere}}}}
</style><main><p class="status">Listing preview · {escape(metadata['status'])}</p>
<h1>{escape(metadata['title'])}</h1><p class="summary">{escape(metadata['summary'])}</p>
<p><a class="download" href="rlp_v3_guard.stl">Download the guard STL</a> &nbsp; <a href="rlp-v3-guard.zip">All print files and source</a></p>
<div class="gallery"><figure><img src="images/rlp-v3-key.jpg" alt="N0SA RLP V3 Morse-code paddle, without a guard"><figcaption>{escape(metadata['photo_caption'])} <a href="{escape(metadata['paddle_reference'])}">Original listing</a>.</figcaption></figure>{figures['hero']}</div>
{description}
<div class="gallery">{figures['nose']}{figures['print_orientation']}</div>
<figure><img src="magnet-pocket.svg" alt="Magnet pocket with a flat seating ring and shallow center glue recess"></figure>
<hr><p><a href="file-descriptions.txt">File notes</a> · <a href="metadata.json">Listing settings</a> · <a href="manifest.json">Build checks</a></p></main></html>'''
    (OUTPUT / "preview.html").write_text(preview)
    for relative, digest in input_hashes.items():
        require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest,
                f"Input changed while packaging: {relative}")
    files = [entry["file"] for entry in meshes] + [f"{v}.png" for v in VIEWS] + [
        "magnet-pocket.svg", "magnet-pocket.png", "description.html", SOURCE.name, "metadata.json",
        "images/rlp-v3-key.jpg", "file-descriptions.txt", "preview.html"]
    hashes = {name: hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest() for name in files}
    manifest = {"status": "prototype", "input_sha256": input_hashes,
                "output_sha256": hashes, "meshes": meshes}
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_zip(OUTPUT / "rlp-v3-guard.zip", {
        name: (OUTPUT / name).read_bytes() for name in files + ["manifest.json"]})
    print(f"Prepared {len(meshes)} checked STLs, reference photo, CAD views and listing preview:\n{OUTPUT}")


if __name__ == "__main__":
    main()
