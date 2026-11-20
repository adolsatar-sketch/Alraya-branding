def skel_d(sk):
    s = f"M{sk.segs[0][0][0]:.1f} {sk.segs[0][0][1]:.1f}"
    for (a, b, c, e) in sk.segs:
        s += f"C{b[0]:.1f} {b[1]:.1f} {c[0]:.1f} {c[1]:.1f} {e[0]:.1f} {e[1]:.1f}"
    return s
