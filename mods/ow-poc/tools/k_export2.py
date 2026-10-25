import bpy, sys, os, numpy as np
A = "/workspace/study/fmrecomp/assets_ext/kenney_survivors/"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=A+"Model/characterMedium.fbx")
arm = bpy.data.objects["Root"]; mesh = bpy.data.objects["characterMedium"]
src = {}
for f in ["idle", "run"]:
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.fbx(filepath=A+f"Animations/{f}.fbx")
    new = [bpy.data.objects[n] for n in set(bpy.data.objects.keys()) - before]
    a = [o for o in new if o.type == "ARMATURE"][0]
    src[f] = a
    act = [x for x in bpy.data.actions if x.name.endswith("|Idle" if f=="idle" else "|Run") and x.name.startswith(a.name)][0]
    a.animation_data.action = act
    try: a.animation_data.action_slot = act.slots[0]
    except Exception as ex: print("slot", ex)
    print(f, [(o.name, o.type) for o in new], a.animation_data.action.name if a.animation_data else None)
sc = bpy.context.scene
out = {}
def pose_from(f, frame):
    s = src[f]
    sc.frame_set(frame); bpy.context.view_layer.update()
    mats = {b.name: b.matrix.copy() for b in s.pose.bones}
    # drive the model's skeleton with the same absolute bone matrices (parents first)
    arm.animation_data_clear()
    order = []
    def walk(b):
        order.append(b)
        for c in b.children: walk(c)
    for b in arm.pose.bones:
        if b.parent is None: walk(b)
    for b in order:
        if b.name in mats:
            b.matrix = mats[b.name]
            bpy.context.view_layer.update()
def grab(f, frame, key):
    pose_from(f, frame)
    dg = bpy.context.evaluated_depsgraph_get(); e = mesh.evaluated_get(dg); me = e.to_mesh()
    me.calc_loop_triangles()
    P = np.array([(mesh.matrix_world @ v.co)[:] for v in me.vertices], np.float32)
    N = np.array([(mesh.matrix_world.to_3x3() @ v.normal)[:] for v in me.vertices], np.float32)
    if "tris" not in out:
        out["tris"] = np.array([t.vertices[:] for t in me.loop_triangles], np.int32)
        uvl = me.uv_layers.active.data
        out["uv"] = np.array([[uvl[l].uv[:] for l in t.loops] for t in me.loop_triangles], np.float32)
    out[key+"_P"] = P; out[key+"_N"] = N
    print(key, frame, P.min(0).round(2), P.max(0).round(2))
    e.to_mesh_clear()
grab("idle", 1, "idle")
for i, fr in enumerate([2, 4, 6, 9, 11, 13][:6]):
    pass
RF = [1, 4, 6, 9, 12, 14]   # run cycle (frames 1..17)
for i, fr in enumerate(RF): grab("run", fr, "run%d" % i)
np.savez("/workspace/study/fmrecomp/sprite_work/kenney_frames.npz", **out)
