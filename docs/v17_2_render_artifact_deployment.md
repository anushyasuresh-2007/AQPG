# AQPG V17.2 Render Artifact Deployment

This document describes delivery of the approved AQPG V17.2 checkpoint to Render without storing model weights in ordinary Git.

## Approved Artifact

The private artifact must be a gzip-compressed tar archive containing exactly this directory and six files:

```text
best_model/
  config.json
  generation_config.json
  model.safetensors
  special_tokens_map.json
  tokenizer.json
  tokenizer_config.json
```

The archive must be controlled by the AQPG project. Do not use a public URL or an uncontrolled model repository.

The deployment verifier requires these file hashes:

| File | SHA-256 |
| --- | --- |
| `config.json` | `8175ff688ac72a8aeb00416a323fb536a51f25b3e4b28eea48ab9efaee3047cd` |
| `generation_config.json` | `196b3297c73e8b686aa1c3bc1fe99b17362ddd682354a710a6f07c697eb6e273` |
| `model.safetensors` | `e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954` |
| `special_tokens_map.json` | `65d84a9271d68f1230ab99518c00f0f7eaef95c7b363001595ba6fa662d434b1` |
| `tokenizer.json` | `8c3804f01b141a4f28649b2ff899f7eb3bedad28fd898f8c38b7dbc70db700bf` |
| `tokenizer_config.json` | `ebc3fede7a53346b49346d8e8fbb7d664b9b448f559660c36195bb19e2d5eaaa` |

## Storage Configuration

Use a private object-storage location controlled by the project. The object may be exposed through an authenticated endpoint or a short-lived signed URL. It must not be publicly readable.

Before creating the Render service, set these Render environment variables:

```text
V17_2_ARTIFACT_URL=<private authenticated artifact URL>
V17_2_ARTIFACT_ARCHIVE_SHA256=<approved SHA-256 of the complete .tar.gz archive>
V17_2_ARTIFACT_TOKEN=<optional bearer token; use only when required by the storage endpoint>
```

`V17_2_ARTIFACT_TOKEN` is a Render secret. Do not put it in `.env`, source control, documentation, or build output. A signed URL is itself sensitive and must also be stored as a Render secret value.

The archive hash is intentionally supplied separately from the six file hashes. The fetcher verifies the archive first, then safely extracts and verifies every expected file. The model hash is hard-coded in the deployment verifier so a wrong configuration cannot silently authorize another model.

## Application Configuration

Required production application variables:

```text
ENVIRONMENT=production
AI_PROVIDER=v17_2
DATABASE_URL=<existing production database URL>
SECRET_KEY=<existing production secret>
BACKEND_CORS_ORIGINS=["https://aqpg.vercel.app"]
```

`V17_2_MODEL_PATH` is optional. The default path must remain:

```text
backend/ml/models/checkpoints/flan_t5_v17_2/best_model
```

Do not set it to a remote location. The V17.2 adapter must continue loading with `local_files_only=True`.

## Render Configuration

```text
Root Directory: backend
Python: 3.10.11
Build Command: pip install -r requirements.txt && python scripts/fetch_v17_2_artifact.py
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The fetch script uses only Python standard-library modules, so no additional dependency is required in `requirements.txt`.

## Verification and Failure Behavior

`backend/scripts/fetch_v17_2_artifact.py`:

1. Requires the private artifact URL and archive SHA-256.
2. Downloads to a temporary file.
3. Does not print the URL, token, or credentials.
4. Rejects unsafe archive paths, links, and unsupported archive entries.
5. Verifies the complete archive SHA-256.
6. Requires exactly the six approved files under `best_model/`.
7. Verifies every file hash, including the required V17.2 weight hash.
8. Installs only after staged verification succeeds.
9. Verifies the installed checkpoint again.
10. Exits nonzero on any missing variable, download error, archive error, path violation, missing file, or hash mismatch.

When `AI_PROVIDER=v17_2`, application startup independently verifies the same six files and hashes before the FastAPI application is created. Startup refuses to continue if the checkpoint is missing or corrupted. No remote model fallback is allowed for V17.2.

The application does not load model weights during this integrity check. Model loading remains local-only and occurs through the existing V17.2 adapter when inference is requested.

## Security Model

- Keep the bucket/object private.
- Use a dedicated read-only storage identity or short-lived signed URL.
- Grant access only to the approved artifact.
- Store credentials only as Render secret environment variables.
- Never log authorization headers, tokens, signed URLs, or secret values.
- Use immutable/versioned object storage so the approved archive cannot change in place.
- Do not upload a model until the artifact hash has been independently reviewed.

## Rollback Procedure

To roll back the application provider without changing model files, set:

```text
AI_PROVIDER=<approved rollback provider>
```

For a V17.2 artifact rollback, point `V17_2_ARTIFACT_URL` and `V17_2_ARTIFACT_ARCHIVE_SHA256` to a previously approved immutable artifact. The six-file manifest and hard-coded model hash must still match the approved V17.2 checkpoint. Never replace V17.2 with V17.1 through this mechanism.

If verification fails, keep the previous running deployment or correct the artifact configuration. Do not bypass verification.

## Deployment Status

The fetcher and startup verification are implemented locally only. The artifact has not been uploaded, GitHub has not been pushed, and Render has not been deployed.
