import os
import json
import hashlib

base_dir = r'c:\Users\Divya\OneDrive\Desktop\AQPG'
train_path = os.path.join(base_dir, 'phase21_step3_v17_train_dataset.jsonl')
val_path = os.path.join(base_dir, 'phase21_step3_v17_validation_dataset.jsonl')

EXPECTED_TRAIN_SHA = 'CFA5B581E0D10D5CD65D7BDB5B0F75D355EE97EDC8F70570ECF12FBB76C7641B'
EXPECTED_VAL_SHA = 'A6BAAA9DEFAFCEDD924DAFA65BAAA19CD7484B776E013CF1D6EAF32ED021CFDF'

with open(train_path, 'rb') as f:
    actual_train_sha = hashlib.sha256(f.read()).hexdigest().upper()

with open(val_path, 'rb') as f:
    actual_val_sha = hashlib.sha256(f.read()).hexdigest().upper()

train_count = 0
with open(train_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip(): train_count += 1

val_count = 0
with open(val_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip(): val_count += 1

train_match = (actual_train_sha == EXPECTED_TRAIN_SHA) and (train_count == 40000)
val_match = (actual_val_sha == EXPECTED_VAL_SHA) and (val_count == 10000)

print('=== DATASET INTEGRITY VERIFICATION ===')
print(f'Train Dataset:      {train_count:,} records | SHA: {actual_train_sha} | Match: {train_match}')
print(f'Validation Dataset: {val_count:,} records | SHA: {actual_val_sha} | Match: {val_match}')

if train_match and val_match:
    print('DATASET VERIFICATION VERDICT: PASS')
else:
    print('DATASET VERIFICATION VERDICT: FAIL')
