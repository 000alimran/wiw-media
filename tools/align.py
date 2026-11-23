"""Find when each script line is spoken, using the pauses in the voiceover (no speech-to-text needed)."""
import subprocess, numpy as np


def _energy(path, sr=16000, hop=0.02):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32)
    h = int(sr * hop); n = len(a) // h
    rms = np.sqrt((a[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-6
    return 20 * np.log10(rms), len(a) / sr, hop


def align(path, lines, min_pause=0.22):
    db, dur, hop = _energy(path)
    thr = max(np.percentile(db, 90) - 32, 25)
    sil = db < thr
    pauses, i, n = [], 0, len(sil)
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            if (j - i) * hop >= min_pause:
                pauses.append((i * hop, j * hop))
            i = j
        else:
            i += 1
    s0 = pauses[0][1] if pauses and pauses[0][0] == 0 else 0.0
    s1 = pauses[-1][0] if pauses and pauses[-1][1] >= dur - hop * 2 else dur
    inner = [p for p in pauses if p[0] > s0 + .1 and p[1] < s1 - .1]
    w = np.array([max(len(l), 4) for l in lines], float)
    cum = np.cumsum(w)[:-1] / w.sum()
    exp = s0 + (s1 - s0) * cum
    K, P = len(exp), len(inner)
    if K == 0:
        bounds = []
    elif P < K:
        bounds = [(e, e) for e in exp]
    else:
        mid = np.array([(a + b) / 2 for a, b in inner]); wid = np.array([b - a for a, b in inner])
        INF = 1e18
        cost = np.full((K, P), INF); back = np.zeros((K, P), int)
        loc = lambda k, p: ((mid[p] - exp[k]) / 4.0) ** 2 - 20 * wid[p]
        for p in range(P):
            cost[0, p] = loc(0, p)
        for k in range(1, K):
            best, arg = INF, -1
            for p in range(P):
                if p - 1 >= 0 and cost[k - 1, p - 1] < best:
                    best, arg = cost[k - 1, p - 1], p - 1
                if arg >= 0:
                    cost[k, p] = best + loc(k, p); back[k, p] = arg
        p = int(np.argmin(cost[K - 1])); chosen = [p]
        for k in range(K - 1, 0, -1):
            p = back[k, p]; chosen.append(p)
        bounds = [inner[p] for p in reversed(chosen)]
    starts = [s0] + [b[1] for b in bounds]
    ends = [b[0] for b in bounds] + [s1]
    return {"duration": round(dur, 3),
            "lines": [{"text": l, "start": round(a, 3), "end": round(b, 3)} for l, a, b in zip(lines, starts, ends)]}


if __name__ == "__main__":
    import sys, json
    print(json.dumps(align(sys.argv[1], sys.argv[2:]), indent=1))
