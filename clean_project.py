import os
import shutil

# Files and directories to clean up
FILES_TO_DELETE = [
    "nul",                  # typo/temporary file
    "errors(CICD).txt",     # temporary CI/CD error log
    "template.py",          # boilerplate folder structure creator
    "update_dataset.py",    # older dataset update script (replaced by update_dataset_real.py)
    "retrain_model.py",     # older training script (replaced by retrain_model_real.py)
]

DIRS_TO_CLEAN = [
    "__pycache__",
    "src/mlproject/__pycache__",
    "src/mlproject/components/__pycache__",
    "src/mlproject/pipelines/__pycache__",
]

def clean():
    print("=== MediSecure Project Cleanup ===")
    
    # 1. Delete files
    for file_path in FILES_TO_DELETE:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[SUCCESS] Deleted file: {file_path}")
            except Exception as e:
                print(f"[ERROR] Could not delete file {file_path}: {e}")
        else:
            print(f"[INFO] File not found (already deleted): {file_path}")
            
    # 2. Delete __pycache__ directories
    for dir_path in DIRS_TO_CLEAN:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"[SUCCESS] Deleted directory: {dir_path}")
            except Exception as e:
                print(f"[ERROR] Could not delete directory {dir_path}: {e}")
        else:
            print(f"[INFO] Directory not found: {dir_path}")

    print("\nCleanup process completed!")

if __name__ == "__main__":
    clean()
