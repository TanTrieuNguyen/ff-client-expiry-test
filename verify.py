#!/usr/bin/env python3
import base64
import gzip
import hashlib
import json
import struct
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
        changes_file = root / 'v2-changes.json'
        if changes_file.exists():
            changes = json.loads(changes_file.read_text())
            title_file = root / 'title-changes.json'
            title = json.loads(title_file.read_text()) if title_file.exists() else None
            offset = title['payload_offset'] if title else 2768
            size = title['payload_size'] if title else 168020
            payload = raw[offset:offset + size]
            assert hashlib.sha256(payload).hexdigest() == (title or changes)['payload_sha256']
            if title:
                assert title['source_v2_sha256'] == changes['payload_sha256']
                table = payload[title['string_table_offset']:title['string_table_offset'] + title['string_table_size']]
                count = struct.unpack_from('<i', table)[0]
                pos = 4
                strings = []
                for _ in range(count):
                    length = shift = 0
                    while True:
                        byte = table[pos]; pos += 1
                        length |= (byte & 127) << shift
                        if byte < 128:
                            break
                        shift += 7
                    strings.append(table[pos:pos + length].decode('utf-8'))
                    pos += length
                assert pos == len(table) and count == 142
                assert strings[67] == strings[69] == title['title'] == 'HDOAN & TT1403'
                node = raw[title['node_offset']:]
                assert len(node) == title['node_size'] == struct.unpack_from('>Q', node, 24)[0]
            for edit in changes['edits']:
                assert list(struct.unpack_from('<ii', payload, edit['offset'])) == edit['after']
            assert len(changes['edits']) == 14
            disabled = [e['method'] for e in changes['edits'] if e['instruction'] == 1 and e['after'] == [136, 0]]
            assert sorted(disabled) == [6, 17, 19, 26]
print('PASS: 72 file hashes, 71 manifest entries, experimental GZIP and raw hash. Runtime NOT tested.')