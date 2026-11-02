"""Build two client-review previews from the v3-audit branch output:
/v3bf/ = V3 + client feedback, /v4bf/ = V4 design + client feedback."""
import os, re, sys, glob, shutil, hashlib, subprocess, tempfile
ROOT = '/home/claude/aamal-website'
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_v4 as B4

tmp = tempfile.mkdtemp()
subprocess.run(f"git -C {ROOT} archive v3-audit v3 assets/css/v3.css assets/js/main.js | tar -x -C {tmp}", shell=True, check=True)
shutil.copy(f"{tmp}/assets/css/v3.css", f"{ROOT}/assets/css/v3bf.css")
shutil.copy(f"{tmp}/assets/js/main.js", f"{ROOT}/assets/js/v3bf.js")
shutil.copy(f"{ROOT}/assets/css/v4.css", f"{ROOT}/assets/css/v4bf.css")
h = lambda p: hashlib.md5(open(f"{ROOT}/{p}", 'rb').read()).hexdigest()[:8]
H3, H4, HJ = h('assets/css/v3bf.css'), h('assets/css/v4bf.css'), h('assets/js/v3bf.js')

def common(s, folder):
    s = re.sub(r'\.\./assets/css/v3\.css\?v=[0-9a-f]+', '../assets/css/v3bf.css?v=' + H3, s)
    s = re.sub(r'\.\./assets/css/v4\.css\?v=[0-9a-f]+', '../assets/css/v4bf.css?v=' + H4, s)
    s = re.sub(r'\.\./assets/js/main\.js(\?v=[0-9a-f]+)?', '../assets/js/v3bf.js?v=' + HJ, s)
    s = s.replace('/aamal-website/v3/', f'/aamal-website/{folder}/').replace('/aamal-website/v4/', f'/aamal-website/{folder}/')
    s = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', s)
    return s

for folder in ('v3bf', 'v4bf'):
    d = f"{ROOT}/{folder}"
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for f in sorted(glob.glob(f"{tmp}/v3/*.html")):
        name = os.path.basename(f); s = open(f, encoding='utf-8').read()
        if folder == 'v4bf':
            s = B4.transform(s, name)
            s = s.replace('One partner for the whole lifecycle', 'From plan to operation')
        open(f"{d}/{name}", 'w', encoding='utf-8').write(common(s, folder))
    print(folder, len(os.listdir(d)))
