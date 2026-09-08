import os
import shutil
import json

src_dir = r'c:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\checkpoints\flan_t5_v17'
archive_dir = r'c:\Users\Divya\OneDrive\Desktop\AQPG\AQPG_V17_CPU_RUN_ARCHIVE_TASK328'

os.makedirs(archive_dir, exist_ok=True)

print('=== INSPECTING AND PRESERVES CPU CHECKPOINTS ===')
preserved_items = []
if os.path.exists(src_dir):
    for item in os.listdir(src_dir):
        ipath = os.path.join(src_dir, item)
        dst_item = os.path.join(archive_dir, item)
        if os.path.isdir(ipath):
            if os.path.exists(dst_item):
                shutil.rmtree(dst_item)
            shutil.copytree(ipath, dst_item)
            preserved_items.append(f'DIR: {item}')
            print(f'  [PRESERVED] Directory: {item}')
        else:
            shutil.copy2(ipath, dst_item)
            preserved_items.append(f'FILE: {item} ({os.path.getsize(ipath)} bytes)')
            print(f'  [PRESERVED] File: {item} ({os.path.getsize(ipath):,} bytes)')

# Write archival metadata manifest
manifest = {
    'archive_name': 'AQPG_V17_CPU_RUN_ARCHIVE_TASK328',
    'reason': 'V17 CPU training interrupted for GPU migration',
    'task_id': 'task-328',
    'stopped_at_timestamp': '2026-08-24T19:26:31Z',
    'base_model': 'google/flan-t5-small',
    'last_known_step': 'checkpoint-250 (Epoch 1)',
    'preserved_items': preserved_items,
    'status': 'V17 CPU training interrupted for GPU migration'
}

with open(os.path.join(archive_dir, 'archive_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print(f'[PASS] Successfully archived all CPU run artifacts to: {archive_dir}')
