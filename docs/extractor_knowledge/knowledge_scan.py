import sys
from pathlib import Path

# ensure local site-packages and src visible even when running with -S
repo_root = Path(__file__).resolve().parents[1]
venv_site_packages = repo_root / ".venv" / "Lib" / "site-packages"
src_dir = repo_root / "src"
for path in (str(venv_site_packages), str(src_dir), str(repo_root)):
    if path not in sys.path:
        sys.path.insert(0, path)

from tools.pyjhora_scanner.run_runner import main


if __name__ == "__main__":
    main()
