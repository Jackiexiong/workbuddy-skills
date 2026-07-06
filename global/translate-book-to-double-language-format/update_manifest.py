
import os
import hashlib
import json

temp_dir = r'test\The House on Mango Street_temp'

def file_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(8192), b''):
            h.update(block)
    return h.hexdigest()

chunks = []
for i in range(1, 11):
    chunk_file = f'chunk{i:04d}.md'
    chunk_path = os.path.join(temp_dir, chunk_file)
    output_file = f'output_chunk{i:04d}.md'
    chunks.append({
        'id': f'chunk{i:04d}',
        'order': i,
        'source_file': chunk_file,
        'source_hash': file_hash(chunk_path),
        'output_file': output_file
    })

manifest = {
    'chunk_count': 10,
    'source_hash': file_hash(os.path.join(temp_dir, 'input.md')),
    'chunks': chunks
}

with open(os.path.join(temp_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print('Updated manifest.json with 10 chunks')

