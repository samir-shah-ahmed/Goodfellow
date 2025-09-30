import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

for cand in ("backend", "Backend"):
    cand_path = os.path.join(ROOT, cand)
    if os.path.isdir(cand_path):
        sys.path.insert(0, cand_path)
        BACKEND_DIR = cand_path
        break
else:
    raise RuntimeError("Couldn't find backend/ or Backend/ folder next to run_api.py")

print("Using BACKEND_DIR:", BACKEND_DIR)

try:
    import app.api.main  # type: ignore
    print("Imported app.api.main OK")
except Exception as e:
    print("Import failed:", e)
    raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="127.0.0.1", port=8000, reload=False)