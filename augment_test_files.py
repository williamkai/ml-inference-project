import os
import shutil
import random
import string

# 設定測試資料夾路徑
TEST_DIR = "./test"

# 每個檔案要複製幾次
NUM_COPIES_PER_FILE = 5

def random_prefix(length=4):
    """產生隨機前綴字串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    # 先列出所有 png 檔
    files = [f for f in os.listdir(TEST_DIR) if f.endswith(".png")]
    
    for f in files:
        label_part = f.split("_label_")[-1]  # 保留 label
        for _ in range(NUM_COPIES_PER_FILE):
            prefix = random_prefix()
            new_name = f"{prefix}_label_{label_part}"
            src_path = os.path.join(TEST_DIR, f)
            dst_path = os.path.join(TEST_DIR, new_name)
            shutil.copy(src_path, dst_path)
            print(f"Copied {f} -> {new_name}")

if __name__ == "__main__":
    main()
