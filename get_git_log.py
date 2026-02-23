import subprocess
result = subprocess.run(["git", "log", "--format=%h | %cd | %s", "--date=local", "-n", "30"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
lines = result.stdout.splitlines()
for line in lines[:5]:
    print(line.encode("ascii", errors="ignore").decode("ascii"))
