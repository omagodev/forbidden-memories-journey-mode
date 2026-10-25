"""Pose keypoints shared by every layer (so all layers align by construction).
Directions: 'down' (front), 'left', 'up' (back); 'right' is the left row mirrored.  Frames 0..4 = idle, step A, idle, step B, idle.
Coordinates are texel edge coordinates (x 0..48 mirrored about 24.0, y 0..62, feet bottom at y=57)."""

def pose(d, f):
    s = {1: 1, 3: -1}.get(f, 0)          # step sign
    p = dict(d=d, f=f, s=s)
    FOOT = 57.0
    if d in ("down", "up"):
        if d == "up": s = -s             # seen from behind the lifted leg is on the other side of the screen
        p.update(head=(24.0, 16.0), torso_y=27.0, hip_y=44.0,
                 legL=(21.7, FOOT - (3.0 if s == 1 else 0.0)), legR=(26.3, FOOT - (3.0 if s == -1 else 0.0)),
                 handL=(15.6, 38.5 + (-1.0 if s == 1 else (1.0 if s == -1 else 0.0))),
                 handR=(32.4, 38.5 + (-1.0 if s == -1 else (1.0 if s == 1 else 0.0))),
                 shL=(16.4, 29.0), shR=(31.6, 29.0), lift=(s,))
    else:  # left view: near = camera side
        near_foot = (22.6 - 4.2 * s, FOOT - (0.0 if s >= 0 else 1.6))
        far_foot = (25.2 + 4.2 * s, FOOT - (1.6 if s > 0 else 0.0)) if s else (25.4, FOOT)
        if s == 0: near_foot = (22.2, FOOT)
        p.update(head=(23.0, 16.0), torso_y=27.0, hip_y=44.0, near_foot=near_foot, far_foot=far_foot,
                 near_hand=(23.6 + 4.0 * s, 38.5 - (0.0 if s <= 0 else 0.6)), far_hand=(24.4 - 4.0 * s, 38.0),
                 sh_near=(23.6, 29.5), sh_far=(24.2, 29.0), s=s)
    return p

DIRS = ["down", "left", "right", "up"]
BASE_DIRS = ["down", "left", "up"]
