"""Storage guardrail utility for VisionSafe AI.
Verifies available disk space on Drive E: and enforces budget policies.
"""
import shutil
import sys
from pathlib import Path

# Safeguard configurations
TARGET_DRIVE = Path("E:/")
MIN_FREE_GB_REQUIRED = 25.0
INITIAL_DATASET_CAP_GB = 15.0

def check_storage() -> bool:
    try:
        total, used, free = shutil.disk_usage(TARGET_DRIVE)
    except Exception as e:
        print(f"[ERROR] Failed to query disk usage for {TARGET_DRIVE}: {e}")
        return False

    total_gb = total / (1024 ** 3)
    free_gb = free / (1024 ** 3)
    used_gb = used / (1024 ** 3)

    print(f"=== VisionSafe AI Storage Check ===")
    print(f"Target Drive        : {TARGET_DRIVE}")
    print(f"Total Disk Space    : {total_gb:.2f} GB")
    print(f"Used Disk Space     : {used_gb:.2f} GB")
    print(f"Free Disk Space     : {free_gb:.2f} GB")
    print(f"Required Free Buffer: {MIN_FREE_GB_REQUIRED:.2f} GB")
    print(f"Initial Raw Cap     : {INITIAL_DATASET_CAP_GB:.2f} GB")
    print("-----------------------------------")

    if free_gb < MIN_FREE_GB_REQUIRED:
        print(f"[GUARD TRIGGERED] Available space ({free_gb:.2f} GB) is below the minimum safe reserve ({MIN_FREE_GB_REQUIRED:.2f} GB)!")
        print("[ACTION] Aborting operation to prevent disk exhaustion.")
        return False

    print(f"[OK] Storage check passed. Safe headroom: {free_gb - MIN_FREE_GB_REQUIRED:.2f} GB above reserve buffer.")
    return True

if __name__ == "__main__":
    if not check_storage():
        sys.exit(1)
    sys.exit(0)
