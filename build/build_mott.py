"""
build_mott.py
Block model for 167 Mott Street from NYC Open Data layers on disk (data/planimetric/*.geojson, trees.json).
Same build as the Clinton, Nostrand and East Village dossiers, pointed at one site, plus stage_building(): 167 Mott itself.
Headless: /Applications/Blender.app/Contents/MacOS/Blender --background --python build/build_mott.py
"""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

OUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in globals() else "/Users/michaelweinfeld/Documents/2026/PJ O'Rourke/Location Research/mott-167"
DATA_DIR = os.path.join(OUT_DIR, "data", "planimetric")
SITE_LAT, SITE_LON = 40.719846, -73.996405
SITES = {"1004710046": ("SITE_167_MOTT", "PJ_BRICK")}
FT = 0.3048; H_FALLBACK = 9.0; COLLECTION = "MOTT_167"
# dark ground; the building in brick, its two shopfronts in 6-train green (Spring St, 278 m). Colours are one line to change.
PALETTE = {"PJ_INK": "2A2724", "PJ_GROUND": "141210", "PJ_ROAD": "1C1A18", "PJ_WALK": "2B2823", "PJ_MEDIAN": "34302A", "PJ_TREE": "4A5A3A", "PJ_BRICK": "8A5A46", "PJ_SITE": "00933C", "PJ_GLASS": "0D1714", "PJ_TRIM": "C9C2B4", "PJ_IRON": "121212", "PJ_SHED": "2F5D3A", "PJ_LABEL": "8A857C"}
COSL = math.cos(math.radians(SITE_LAT))

def proj(lon, lat): return ((lon - SITE_LON) * 111320.0 * COSL, (lat - SITE_LAT) * 110540.0)
def hex_to_linear(h):
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i+2], 16) / 255.0; out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (out[0], out[1], out[2], 1.0)
def make_materials():
    for name, hexc in PALETTE.items():
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if b: b.inputs["Base Color"].default_value = hex_to_linear(hexc); b.inputs["Roughness"].default_value = 0.95
        m.diffuse_color = hex_to_linear(hexc)
def load(key): return json.load(open(os.path.join(DATA_DIR, key + ".geojson")))["features"]
def rings(geom):
    t = geom.get("type"); c = geom.get("coordinates", [])
    if t == "Polygon": return [c[0]] if c else []
    if t == "MultiPolygon": return [p[0] for p in c if p]
    return []
def contours(geom):
    t = geom.get("type"); c = geom.get("coordinates", [])
    src = [c] if t == "Polygon" else (c if t == "MultiPolygon" else [])
    for poly in src:
        out = []
        for ring in poly:
            pts = [proj(a, b) for a, b in ring]; cl = []
            for p in pts:
                if not cl or abs(p[0]-cl[-1][0]) > 1e-7 or abs(p[1]-cl[-1][1]) > 1e-7: cl.append(p)
            if len(cl) > 2 and abs(cl[0][0]-cl[-1][0]) < 1e-7 and abs(cl[0][1]-cl[-1][1]) < 1e-7: cl = cl[:-1]
            if len(cl) >= 3: out.append(cl)
        if out: yield out
def get_collection():
    old = bpy.data.collections.get(COLLECTION)
    if old:
        for o in list(old.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old)
    col = bpy.data.collections.new(COLLECTION); bpy.context.scene.collection.children.link(col); return col
def col(): return bpy.data.collections.get(COLLECTION) or get_collection()

def extrude_ring(bm, xy, z0, z1):
    cl = []
    for p in xy:
        if not cl or abs(p[0]-cl[-1][0]) > 1e-6 or abs(p[1]-cl[-1][1]) > 1e-6: cl.append(p)
    if len(cl) > 2 and abs(cl[0][0]-cl[-1][0]) < 1e-6 and abs(cl[0][1]-cl[-1][1]) < 1e-6: cl = cl[:-1]
    if len(cl) < 3: return False
    vs = [bm.verts.new((p[0], p[1], z0)) for p in cl]
    try: face = bm.faces.new(vs)
    except ValueError: return False
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, 0, z1 - z0), verts=[v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)])
    return True

def stage_massing():
    make_materials(); c = get_collection(); feats = load("footprints")
    bases = [float(f["properties"].get("ground_elevation") or 0) for f in feats if f["properties"].get("base_bbl") in SITES]
    base = sum(bases) / len(bases) if bases else 0.0
    bm = bmesh.new(); sbms = {k: bmesh.new() for k in SITES}; n = 0; guessed = 0
    for f in feats:
        p = f["properties"]
        try: h_ft = float(p.get("height_roof") or 0)
        except ValueError: h_ft = 0.0
        h = h_ft * FT
        if h <= 0: h = H_FALLBACK; guessed += 1
        ge = (float(p.get("ground_elevation") or base) - base) * FT
        target = sbms.get(p.get("base_bbl"), bm)
        for ring in rings(f["geometry"]):
            if extrude_ring(target, [proj(a, b) for a, b in ring], ge, ge + h): n += 1
    for b, name, mat in [(bm, "NOLITA_MASSING", "PJ_INK")] + [(sbms[k], SITES[k][0], SITES[k][1]) for k in SITES]:
        bmesh.ops.recalc_face_normals(b, faces=b.faces); me = bpy.data.meshes.new(name); b.to_mesh(me); b.free()
        ob = bpy.data.objects.new(name, me); c.objects.link(ob); ob.data.materials.append(bpy.data.materials[mat])
    return "massing: {} solids, {} without height".format(n, guessed)

def build_flat(key, name, z, mat):
    feats = load(key); verts, faces = [], []
    for f in feats:
        for cont in contours(f["geometry"]):
            vecs = [[Vector((x, y, 0.0)) for (x, y) in ring] for ring in cont]; flat = [v for ring in vecs for v in ring]; b = len(verts)
            try: idx = tessellate_polygon(vecs)
            except Exception: continue
            verts.extend([(v.x, v.y, z) for v in flat]); faces.extend([(b+t[0], b+t[1], b+t[2]) for t in idx])
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); col().objects.link(ob); ob.data.materials.append(bpy.data.materials[mat])
    return "{}: {} tris".format(name, len(faces))
def stage_flat():
    return "; ".join([build_flat("roadbed", "ROADBED", 0.02, "PJ_ROAD"), build_flat("sidewalk", "SIDEWALK", 0.14, "PJ_WALK"), build_flat("median", "MEDIAN", 0.18, "PJ_MEDIAN")])

def at_fraction(pts, frac):
    segs = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]; total = sum(segs); want = total * frac; run = 0.0
    for i, s in enumerate(segs):
        if run + s >= want:
            t = (want - run) / s if s else 0.0; a, b = pts[i], pts[i+1]
            return ((a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t), math.atan2(b[1]-a[1], b[0]-a[0]))
        run += s
    return pts[-1], math.atan2(pts[-1][1]-pts[0][1], pts[-1][0]-pts[0][0])
def stage_labels(size=12.0, min_gap=34.0):
    feats = load("centerline"); longest = {}
    for f in feats:
        n = (f["properties"].get("stname_label") or "").strip()
        if not n: continue
        g = f["geometry"]; parts = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for line in parts:
            pts = [proj(a, b) for a, b in line]; L = sum(math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1))
            if n not in longest or L > longest[n][0]: longest[n] = (L, pts)
    placed = []
    for name, (L, pts) in sorted(longest.items(), key=lambda kv: -kv[1][0]):
        if L < 40: continue
        spot = None
        for frac in (0.5, 0.3, 0.7, 0.18, 0.82):
            p, ang = at_fraction(pts, frac)
            if all(math.dist(p, q) > min_gap for q in placed): spot = (p, ang); break
        if spot is None: spot = at_fraction(pts, 0.5)
        p, ang = spot
        if ang > math.pi/2: ang -= math.pi
        if ang < -math.pi/2: ang += math.pi
        cu = bpy.data.curves.new("ST_" + name, type='FONT'); cu.body = name; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.size = size; cu.extrude = 0.04; cu.space_character = 1.15
        ob = bpy.data.objects.new("ST_" + name, cu); col().objects.link(ob); ob.location = (p[0], p[1], 0.6); ob.rotation_euler = (0, 0, ang); ob.data.materials.append(bpy.data.materials["PJ_LABEL"]); placed.append(p)
    return "labels: {}".format(len(placed))

def stage_trees():
    rows = [r for r in json.load(open(os.path.join(DATA_DIR, "trees.json"))) if r.get("status") == "Alive"]
    bm = bmesh.new(); n = 0
    for t in rows:
        try: x, y = proj(float(t["longitude"]), float(t["latitude"])); dbh = float(t.get("tree_dbh") or 6)
        except (TypeError, ValueError, KeyError): continue
        r = max(1.4, min(4.2, 1.2 + dbh * 0.12)); h = max(4.0, min(11.0, 3.5 + dbh * 0.35))
        tb = bmesh.new(); bmesh.ops.create_icosphere(tb, subdivisions=1, radius=1.0); bmesh.ops.scale(tb, vec=(r, r, r * 0.8), verts=tb.verts); bmesh.ops.translate(tb, vec=(x, y, h), verts=tb.verts)
        me = bpy.data.meshes.new("t"); tb.to_mesh(me); tb.free(); bm.from_mesh(me); bpy.data.meshes.remove(me); n += 1
    me = bpy.data.meshes.new("TREES"); bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new("TREES", me); col().objects.link(ob); ob.data.materials.append(bpy.data.materials["PJ_TREE"])
    return "trees: {}".format(n)

def stage_ground():
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -0.3)); g = bpy.context.active_object; g.name = "GROUND"
    for c in g.users_collection: c.objects.unlink(g)
    col().objects.link(g); g.data.materials.append(bpy.data.materials["PJ_GROUND"]); return "ground"

# ---------- 167 Mott itself ----------
# Body = the city's own outline at the recorded roof height (83.5 ft, 7 floors). Facade detail sits on the Mott St (east) face.
# INFERRED, no photo yet: two ~10 ft shopfronts either side of a centre residential door (listing: 10 ft frontage each,
# PLUTO: 25.33 ft lot front, 2 commercial units), four window bays, centre fire escape, cornice. Replace when photographed.
FRONT_S = (-73.996289633705, 40.719763967702); FRONT_N = (-73.996262656451, 40.719830735139)
ROOF = 83.5 * FT; GF = 12 * FT; NFL = 7
def _box(bm, x0, x1, y0, y1, z0, z1):
    vs = [bm.verts.new(p) for p in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([vs[i] for i in f])
def stage_building():
    for o in [o for o in bpy.data.objects if o.name.startswith("B167_")]: bpy.data.objects.remove(o, do_unlink=True)
    a = proj(*FRONT_S); b = proj(*FRONT_N); W = math.dist(a, b); ang = math.atan2(b[1]-a[1], b[0]-a[0])
    parts = {k: bmesh.new() for k in ("PJ_SITE", "PJ_GLASS", "PJ_TRIM", "PJ_IRON", "PJ_BRICK")}
    # local frame: x along the front south to north, -y out over the sidewalk, z up
    pier = 0.30; door_w = 1.10; shop = (W - 2*pier - door_w) / 2          # ~10 ft each
    bays = ((pier, pier + shop, "S"), (pier + shop + door_w, W - pier, "N"))
    for x0, x1, tag in bays:
        _box(parts["PJ_GLASS"], x0 + 0.08, x1 - 0.08, -0.02, 0.10, 0.50, GF - 0.75)        # shop glass
        _box(parts["PJ_SITE"], x0, x1, -0.06, 0.05, 0.0, 0.50)                              # bulkhead
        _box(parts["PJ_SITE"], x0, x1, -0.14, 0.05, GF - 0.75, GF - 0.10)                   # sign band
        for xx in (x0, x1 - 0.08): _box(parts["PJ_SITE"], xx, xx + 0.08, -0.06, 0.05, 0.50, GF - 0.75)
        dx = x1 - 1.0 if tag == "S" else x0 + 0.08                                          # shop door beside the centre entrance
        _box(parts["PJ_SITE"], dx, dx + 0.92, -0.04, 0.04, 0.0, 2.15); _box(parts["PJ_GLASS"], dx + 0.10, dx + 0.82, -0.06, 0.02, 0.25, 2.05)
    for x0, x1 in ((0, pier), (W - pier, W)): _box(parts["PJ_TRIM"], x0, x1, -0.10, 0.05, 0.0, GF)   # end piers
    cx0 = pier + shop
    _box(parts["PJ_IRON"], cx0 + 0.10, cx0 + door_w - 0.10, -0.03, 0.05, 0.0, 2.30)         # residential door
    _box(parts["PJ_TRIM"], cx0, cx0 + door_w, -0.10, 0.05, 2.30, GF - 0.10)
    _box(parts["PJ_TRIM"], 0, W, -0.22, 0.05, GF - 0.10, GF + 0.18)                         # storefront cornice
    fh = (ROOF - GF) / (NFL - 1)
    for fl in range(NFL - 1):
        z = GF + fl * fh
        for i in range(4):
            c = W * (i + 0.5) / 4
            _box(parts["PJ_GLASS"], c - 0.46, c + 0.46, -0.03, 0.05, z + 0.85, z + 2.75)
            _box(parts["PJ_TRIM"], c - 0.56, c + 0.56, -0.10, 0.05, z + 0.73, z + 0.85)     # sill
            _box(parts["PJ_TRIM"], c - 0.56, c + 0.56, -0.08, 0.05, z + 2.75, z + 2.98)     # lintel
        # fire escape on the two centre bays
        fx0, fx1 = W * 0.25 - 0.55, W * 0.75 + 0.55
        _box(parts["PJ_IRON"], fx0, fx1, -1.05, 0.0, z + 0.55, z + 0.60)
        _box(parts["PJ_IRON"], fx0, fx1, -1.05, -1.02, z + 1.45, z + 1.49)
        for xx in (fx0, fx1 - 0.03): _box(parts["PJ_IRON"], xx, xx + 0.03, -1.05, 0.0, z + 1.45, z + 1.49)
        n = 14
        for k in range(n + 1):
            xx = fx0 + (fx1 - fx0 - 0.02) * k / n; _box(parts["PJ_IRON"], xx, xx + 0.02, -1.05, -1.03, z + 0.60, z + 1.45)
        if fl < NFL - 2:                                                                    # stair up to the next landing
            for k in range(10):
                t = k / 9; _box(parts["PJ_IRON"], W * 0.5 - 0.9 + 1.8 * t, W * 0.5 - 0.9 + 1.8 * t + 0.22, -0.80, -0.25, z + 0.60 + (fh - 0.05) * t, z + 0.63 + (fh - 0.05) * t)
    _box(parts["PJ_IRON"], W * 0.25 - 0.3, W * 0.25 - 0.25, -1.0, -0.6, GF + 0.2, GF + 0.60 + 0.55)  # drop ladder stub
    _box(parts["PJ_TRIM"], -0.05, W + 0.05, -0.55, 0.05, ROOF - 0.95, ROOF - 0.15)          # cornice
    _box(parts["PJ_TRIM"], -0.10, W + 0.10, -0.70, 0.05, ROOF - 0.15, ROOF + 0.10)
    _box(parts["PJ_BRICK"], 0, W, 0.0, 0.35, ROOF, ROOF + 0.9)                              # parapet
    root = bpy.data.objects.new("B167_FACADE", None); col().objects.link(root); root.location = (a[0], a[1], 0.14); root.rotation_euler = (0, 0, ang)
    for mat, bm in parts.items():
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new("B167_" + mat); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new("B167_" + mat[3:], me); col().objects.link(ob); ob.parent = root; ob.data.materials.append(bpy.data.materials[mat])
    # sidewalk shed: permit of 2 July 2024 (DOB NOW, MNK Enterprises), facade violation still active June 2025. Hidden until seen at the door.
    sb = bmesh.new(); _box(sb, -0.3, W + 0.3, -2.6, -0.05, 2.75, 2.95); _box(sb, -0.3, W + 0.3, -2.6, -2.5, 2.95, 4.15)
    for xx in (-0.3, W * 0.33, W * 0.66, W + 0.2):
        for yy in (-2.6, -0.2): _box(sb, xx, xx + 0.1, yy, yy + 0.1, 0.0, 2.75)
    me = bpy.data.meshes.new("B167_SHED"); sb.to_mesh(me); sb.free(); shed = bpy.data.objects.new("B167_SHED_permit_2024", me); col().objects.link(shed); shed.parent = root
    shed.data.materials.append(bpy.data.materials["PJ_SHED"]); shed.hide_viewport = True; shed.hide_render = True
    return "building: front {:.2f} m ({:.1f} ft), roof {:.1f} m, shop bays {:.2f} m each; shed hidden".format(W, W / FT, ROOF, shop)

def stage_cameras():
    sc = bpy.context.scene
    if not bpy.data.objects.get("SUN"):
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 300)); s = bpy.context.active_object; s.name = "SUN"; s.data.energy = 3.0; s.rotation_euler = (math.radians(50), 0, math.radians(35))
    w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg: bg.inputs[0].default_value = (0.08, 0.075, 0.07, 1); bg.inputs[1].default_value = 1.0
    for name, loc, rot, ortho in (("CAM_PLAN", (0, 0, 600), (0, 0, math.radians(29)), 560), ("CAM_WIDE", (0, 0, 600), (0, 0, math.radians(29)), 900)):
        cam = bpy.data.objects.get(name)
        if not cam:
            cd = bpy.data.cameras.new(name); cam = bpy.data.objects.new(name, cd); sc.collection.objects.link(cam)
        cam.location = loc; cam.rotation_euler = rot; cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho; cam.data.clip_end = 2000
    axon = bpy.data.objects.get("CAM_AXON")
    if not axon:
        cd = bpy.data.cameras.new("CAM_AXON"); axon = bpy.data.objects.new("CAM_AXON", cd); sc.collection.objects.link(axon)
    axon.location = (-260, -420, 420); axon.rotation_euler = (math.radians(50), 0, math.radians(-29)); axon.data.type = 'ORTHO'; axon.data.ortho_scale = 700; axon.data.clip_end = 3000
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'):
        if eng in engines:
            try: sc.render.engine = eng; break
            except TypeError: continue
    sc.render.resolution_x = 1800; sc.render.resolution_y = 1200; sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
    return "cameras: plan, wide, axon; engine " + sc.render.engine

def render(cam_name, filename):
    sc = bpy.context.scene; sc.camera = bpy.data.objects[cam_name]; os.makedirs(os.path.join(OUT_DIR, "frames"), exist_ok=True)
    sc.render.filepath = os.path.join(OUT_DIR, "frames", filename)
    bpy.ops.render.render(write_still=True); return "rendered " + sc.render.filepath

def export_glb(filename="mott_167.glb"):
    for o in bpy.data.objects: o.select_set(False)
    names = ["NOLITA_MASSING", "SITE_167_MOTT", "ROADBED", "SIDEWALK", "MEDIAN", "GROUND", "TREES"] + [o.name for o in bpy.data.objects if o.name.startswith("ST_") or (o.name.startswith("B167_") and not o.hide_viewport)]
    for n in names:
        o = bpy.data.objects.get(n)
        if o: o.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["NOLITA_MASSING"]
    path = os.path.join(OUT_DIR, "assets", filename); os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6, export_apply=True, export_cameras=False, export_lights=False, export_yup=True)
    return "exported {} {:.0f} KB".format(path, os.path.getsize(path) / 1024)

def site_center():
    """glTF-space position of the site (x east, y up, z south) for the page's camera waypoints."""
    ob = bpy.data.objects.get("SITE_167_MOTT")
    if not ob or not ob.data.vertices: return None
    xs = [v.co.x for v in ob.data.vertices]; ys = [v.co.y for v in ob.data.vertices]
    return [round(sum(xs)/len(xs), 1), 0, round(-sum(ys)/len(ys), 1)]

if __name__ == "__main__" or bpy.app.background:
    # fresh scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    log = []
    for fn in (stage_massing, stage_flat, stage_labels, stage_trees, stage_ground, stage_building, stage_cameras):
        log.append(fn()); print(log[-1], flush=True)
    # transit points in the same frame, for the page
    pts = {"site": site_center(), "bowery_jz": [round(v, 1) for v in proj(-73.993915, 40.72028)], "spring_6": [round(v, 1) for v in proj(-73.997141, 40.722301)],
           "grand_bd": [round(v, 1) for v in proj(-73.993753, 40.718267)], "canal_st": [round(v, 1) for v in proj(-74.000193, 40.718803)]}
    json.dump(pts, open(os.path.join(OUT_DIR, "data", "model_points.json"), "w")); print("points", pts, flush=True)
    for cam, fn in (("CAM_PLAN", "map_plan.jpg"), ("CAM_AXON", "map_axon.jpg"), ("CAM_WIDE", "map_wide.jpg")):
        try: print(render(cam, fn), flush=True)
        except Exception as e: print("render failed", cam, e, flush=True)
    try: print(export_glb(), flush=True)
    except Exception as e: print("export failed", e, flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "build", "mott_167.blend"))
    print("BUILD DONE", flush=True)
