# AGENTS.md

## Cursor Cloud specific instructions

This repository (`asifahmad11996/gif`) is a **static asset repository**: all tracked files are
`.gif` images in the repo root. There is no application code, package manifest, build system,
lockfile, test suite, or external service.

- **Nothing to install / build / lint / test.** There are no dependencies. Any setup/update
  script is effectively a no-op.
- **How to "run" it:** serve the GIFs over HTTP using Python's built-in server (Python 3 is
  available system-wide), then open `http://localhost:8000/` for a directory listing or
  `http://localhost:8000/<name>.gif` to view an individual image:

  ```
  python3 -m http.server 8000
  ```

- The GIFs are meant to be consumed as static files (e.g. embedded via raw URLs). Validate an
  asset with `file <name>.gif` (expect `GIF image data, version 89a`).
