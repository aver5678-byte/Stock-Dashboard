import os

search_str = "登頂逃命窗口觀測儀"
path = r"c:\Users\user\Desktop\AI代理專案\股市乖離分析\page_biz_cycle.py"

encodings = ["utf-8", "big5", "gbk", "utf-16"]
for enc in encodings:
    try:
        with open(path, "r", encoding=enc) as f:
            content = f.read()
            if search_str in content:
                print(f"Found with {enc}")
                import re
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if search_str in line:
                        print(f"Line {i+1}: {line}")
    except:
        pass
