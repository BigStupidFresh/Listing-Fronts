from pathlib import Path
import base64, hashlib, json, subprocess

m = json.loads(Path("Transfer/fanuc-v24/manifest.json").read_text())
parts = []
for p in m["chunks"]:
    data = Path(p["path"]).read_bytes()
    assert len(data) == p["characters"]
    assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == p["expected_blob_sha"]
    parts.append(data)
data = base64.b64decode(b"".join(parts), validate=True)
assert len(data) == m["bytes"]
assert hashlib.sha256(data).hexdigest() == m["sha256"]
assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == m["git_blob_sha"]
p = Path(m["target"])
p.parent.mkdir(parents=True, exist_ok=True)
p.write_bytes(data)
assert p.read_bytes() == data
print(json.dumps({k: m[k] for k in ["target", "bytes", "sha256", "git_blob_sha"]}))
subprocess.run(["git", "add", "--", str(p)], check=True)
subprocess.run(["git", "rm", "-r", "--", "Transfer/fanuc-v24", ".github/workflows/fanuc-v24-image-transfer.yml"], check=True)
subprocess.run(["git", "-c", "user.name=github-actions[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com", "commit", "-m", "Reconstruct verified corrected FANUC stock image"], check=True)
subprocess.run(["git", "push", "origin", "HEAD:refs/heads/assets/fanuc-v24-transfer-20261022"], check=True)
