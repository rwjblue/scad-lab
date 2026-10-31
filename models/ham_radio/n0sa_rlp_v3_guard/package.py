#!/usr/bin/env python3
"""Prepare local Printables assets; never upload, publish or alter the guard."""
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
OUTPUT = ROOT / "output/printables/n0sa-rlp-v3-guard"
SIZES = {"guard": [41.67, 35.07, 41.47],
         "fit_coupon": [41.67, 10.24, 5.42], "magnet_gauge": [28, 14, 3.3]}
VIEWS = {
    "hero": ("70,-85,65,0,8,12", "Open rear: continuous floor and two magnet pockets. CAD render."),
    "nose": ("65,90,55,0,8,12", "Closed bumper and tapered exterior. CAD render."),
    "print_orientation": ("70,-90,75,0,17,20", "Print closed nose down, opening up; supports off for the next trial. CAD render."),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def openscad(output, source, definitions=(), image_camera=None):
    command = ["openscad", "--backend=Manifold", "--hardwarnings"]
    if image_camera:
        command += ["--render", "--imgsize=2000,1500", "--projection=ortho",
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


def export_mesh(job):
    part, thickness = job
    suffix = {1.5: "1p5", 2.0: "2p0"}[thickness]
    name = f"rlp_v3_{part}_6x{suffix}.stl"
    output = OUTPUT / name
    definitions = [f'part="{part}"', f"insert_thickness={thickness}",
                   'print_orientation="nose_down"']
    openscad(output, SOURCE, definitions)
    mesh = trimesh.load_mesh(output)
    require(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0,
            f"Invalid mesh: {name}")
    components = len(mesh.split(only_watertight=False))
    require(components == 1, f"Disconnected mesh: {name}")
    require(np.allclose(mesh.extents, SIZES[part], atol=0.001) and
            abs(mesh.bounds[0, 2]) < 0.001, f"Unexpected dimensions/bed position: {name}")
    purpose = {"guard": "Full guard; print one, nose-down",
               "fit_coupon": "Optional underside alignment coupon; floor-down",
               "magnet_gauge": "Optional diameter gauge; notched end is looser; floor-down"}[part]
    return {"file": name, "description": f"{purpose}. For 6 x {thickness:g} mm magnets.",
            "definitions": definitions, "size_mm": mesh.extents.tolist(),
            "bounds_mm": mesh.bounds.tolist(), "watertight": True,
            "winding_consistent": True, "connected_solids": components}


def magnet_diagram():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
<rect width="1600" height="1000" fill="#f7f7f5"/>
<g font-family="Arial, sans-serif" fill="#20252b">
<text x="90" y="105" font-size="48" font-weight="700">Two magnets. Choose one thickness.</text>
<text x="90" y="158" font-size="27">6 mm diameter · axially magnetized · install after printing</text>
<g transform="translate(100,230)">
<text y="35" font-size="32" font-weight="700">6 × 2 mm — primary test</text>
<path d="M0 120H75V335H545V120H620V450H0Z" fill="#c75929"/>
<rect x="85" y="135" width="450" height="200" rx="5" fill="#aab2bd"/>
<text x="310" y="250" text-anchor="middle" font-size="38">2.00 mm disc</text>
<path d="M660 120V335M648 120H672M648 335H672" stroke="#20252b" stroke-width="3"/>
<text x="310" y="500" text-anchor="middle" font-size="28">Pocket 2.15 mm deep</text>
<text x="310" y="545" text-anchor="middle" font-size="26">1.15 mm plastic below</text>
</g>
<g transform="translate(870,230)">
<text y="35" font-size="32" font-weight="700">6 × 1.5 mm — alternative</text>
<path d="M0 120H75V285H545V120H620V450H0Z" fill="#c75929"/>
<rect x="85" y="135" width="450" height="150" rx="5" fill="#aab2bd"/>
<text x="310" y="230" text-anchor="middle" font-size="38">1.50 mm disc</text>
<text x="310" y="500" text-anchor="middle" font-size="28">Pocket 1.65 mm deep</text>
<text x="310" y="545" text-anchor="middle" font-size="26">1.65 mm plastic below</text>
</g>
<text x="90" y="855" font-size="27">Both: Ø6.20 mm pocket · 0.15 mm face recess · 3.30 mm floor</text>
<text x="90" y="905" font-size="27" font-weight="700">Match each magnet’s polarity to its corresponding key magnet before gluing.</text>
<text x="90" y="955" font-size="22" fill="#606973">Schematic, not to scale. Guard fit and retention validation pending. N1RWJ · V6</text>
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
    inputs = [SOURCE, HERE / "README.md", Path(__file__).resolve(),
              *sorted(MARKETING.iterdir())]
    input_hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in inputs if path.is_file()}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((MARKETING / "metadata.json").read_text())
    jobs = [(part, thickness) for part in SIZES for thickness in [2.0, 1.5]]
    with ThreadPoolExecutor(max_workers=4) as pool:
        meshes = list(pool.map(export_mesh, jobs))
    for view, (camera, _) in VIEWS.items():
        openscad(OUTPUT / f"{view}.png", MARKETING / "views.scad",
                 [f'view="{view}"', "insert_thickness=2.0"], camera)
    (OUTPUT / "magnet-options.svg").write_text(magnet_diagram())
    with pymupdf.open(OUTPUT / "magnet-options.svg") as vector:
        with pymupdf.open(stream=vector.convert_to_pdf(), filetype="pdf") as drawing:
            scale = 2000 / drawing[0].rect.width
            drawing[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale)).save(
                OUTPUT / "magnet-options.png")
    description = (MARKETING / "printables.html").read_text()
    (OUTPUT / "description.html").write_text(description)
    (OUTPUT / SOURCE.name).write_bytes(SOURCE.read_bytes())
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    guide = (HERE / "README.md").read_text().split("## Printables preparation")[0]
    (OUTPUT / "PRINT-AND-FIT.txt").write_text(guide)
    (OUTPUT / "file-descriptions.txt").write_text("\n\n".join(
        f"{entry['file']}\n{entry['description']}" for entry in meshes) +
        f"\n\n{SOURCE.name}\nSelf-contained editable OpenSCAD source; defaults to 1.5 mm inserts.\n")
    images = "".join(f'<figure><img src="{view}.png" alt="{escape(caption)}">'
                     f'<figcaption>{escape(caption)}</figcaption></figure>'
                     for view, (_, caption) in VIEWS.items())
    preview = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(metadata['title'])} — publication draft</title>
<style>body{{font:17px/1.6 system-ui,sans-serif;color:#252b31;background:#f7f7f5;margin:0}}
main{{max-width:1040px;margin:auto;padding:40px 32px}}h1{{font-size:38px;line-height:1.15}}
h3{{margin-top:2em}}a{{color:#99411e}}.status{{padding:12px 18px;background:#fae8d8;border-left:4px solid #c75929}}
table{{border-collapse:collapse;width:100%;font-size:15px}}th,td{{border:1px solid #d2d5d7;padding:10px;text-align:left}}
figure{{margin:24px 0}}img{{display:block;width:100%;height:auto}}figcaption{{color:#5b626b;font-size:14px}}
.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}.gallery figure{{margin:0}}
@media(max-width:700px){{.gallery{{display:block}}main{{padding:24px 16px}}h1{{font-size:30px}}table{{font-size:12px}}}}
</style><main><p class="status"><strong>LOCAL DRAFT · V6</strong> — physical fit validation pending; not published.</p>
<h1>{escape(metadata['title'])}</h1><p>{escape(metadata['summary'])}</p><div class="gallery">{images}</div>
<figure><img src="magnet-options.svg" alt="Magnet thickness and matching blind-pocket dimensions"><figcaption>Magnet selection and pocket cross-sections; schematic.</figcaption></figure>
{description}<hr><p>Upload preparation: <a href="file-descriptions.txt">per-file notes</a> · <a href="metadata.json">metadata and proposed license</a> · <a href="manifest.json">mesh checks and hashes</a></p></main></html>'''
    (OUTPUT / "preview.html").write_text(preview)
    for relative, digest in input_hashes.items():
        require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest,
                f"Input changed while packaging: {relative}")
    files = [entry["file"] for entry in meshes] + [f"{v}.png" for v in VIEWS] + [
        "magnet-options.svg", "magnet-options.png", "description.html", SOURCE.name, "metadata.json",
        "PRINT-AND-FIT.txt", "file-descriptions.txt", "preview.html"]
    hashes = {name: hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest() for name in files}
    manifest = {"status": "draft_requires_physical_fit", "revision": "V6",
                "input_sha256": input_hashes, "output_sha256": hashes, "meshes": meshes}
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_zip(OUTPUT / "rlp-v3-editable-source.zip", {
        SOURCE.name: SOURCE.read_bytes(), "PRINT-AND-FIT.txt": (OUTPUT / "PRINT-AND-FIT.txt").read_bytes()})
    payloads = {name: (OUTPUT / name).read_bytes() for name in files + ["manifest.json"]}
    write_zip(OUTPUT / "rlp-v3-printables-draft.zip", payloads)
    print(f"Prepared {len(meshes)} checked STLs, three CAD images, magnet diagram and local draft:\n{OUTPUT}")


if __name__ == "__main__":
    main()
