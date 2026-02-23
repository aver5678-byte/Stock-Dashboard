import os

search_str = "獲利黃金期"
root_dir = r"c:\Users\user\Desktop\AI代理專案\股市乖離分析"

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if search_str in content:
                        print(f"Found in: {path}")
            except:
                try:
                    with open(path, "r", encoding="big5") as f:
                        content = f.read()
                        if search_str in content:
                            print(f"Found in: {path}")
                except:
                    pass
