"""Build automation script for packaging Elenchus standalone binary."""

import os
import subprocess
import sys


def build() -> int:
    """Run PyInstaller with packaging/elenchus.spec and report build status.

    :return: Process exit code integer.
    """
    spec_path = os.path.join(os.path.dirname(__file__), "elenchus.spec")
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist"))

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        f"--distpath={dist_dir}",
        spec_path,
    ]

    print(f"[Elenchus Build] Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n[Elenchus Build] Build succeeded!")
        print(f"[Elenchus Build] Standalone binary output: {dist_dir}")
    else:
        print(f"\n[Elenchus Build] Build failed with exit code {result.returncode}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
