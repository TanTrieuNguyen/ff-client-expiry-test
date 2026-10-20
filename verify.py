#!/usr/bin/env python3
import base64
import gzip
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
index = json.loads((root / 'integrity.json').read_text())
assert len(index['files']) == 72
for entry in index['files']:
    data = (root / 'raw' / entry['route'].lstrip('/')).read_bytes()
    assert len(data) == entry['size'], entry['route']
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], entry['route']
rows = (root / 'raw/ios/1.132.11/fileinfo').read_text().splitlines()
assert len(rows) == 71
for row in rows:
    fields = row.split(',')
    suffix = fields[4].replace('+', '~2B').replace('/', '~2F').replace('=', '~3D')
    filename = root / 'raw/ios/1.132.11/gameassetbundles' / (fields[0] + '.' + suffix)
    data = filename.read_bytes()
    assert len(data) == int(fields[5]), fields[0]
    assert base64.b64encode(hashlib.sha1(data).digest()).decode() == fields[4], fields[0]
    if fields[0] == 'codepatch/assembly-csharp-patch':
        raw = gzip.decompress(data)
        assert len(raw) == int(fields[2])
        assert base64.b64encode(hashlib.sha1(raw).digest()).decode() == fields[1]
print('PASS: 72 file hashes, 71 manifest entries, experimental GZIP and raw hash. Runtime NOT tested.')