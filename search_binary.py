import os

search_str = "獲利黃金期"
root_dir = r"c:\Users\user\Desktop\AI代理專案\股市乖離分析"

for root, dirs, files in os.walk(root_dir):
    for file in files:
        path = os.path.join(root, file)
        try:
            with open(path, "rb") as f:
                content = f.read()
                if search_str.encode("utf-8") in content or search_str.encode("big5") in content:
                    print(f"Found in: {path}")
        except:
            pass
