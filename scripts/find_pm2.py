import subprocess

def main():
    # We will search for pm2.cmd in C:\Users\roberto and C:\Users\gemini
    cmds = [
        ["ssh", "roberto@192.168.1.139", "powershell -Command \"Get-ChildItem -Path C:\\Users\\roberto -Filter pm2.cmd -Recurse -ErrorAction SilentlyContinue | Select-Object FullName\""],
        ["ssh", "roberto@192.168.1.139", "powershell -Command \"Get-ChildItem -Path C:\\Users\\gemini -Filter pm2.cmd -Recurse -ErrorAction SilentlyContinue | Select-Object FullName\""]
    ]
    for idx, cmd in enumerate(cmds):
        print(f"=== Command {idx+1} ===")
        try:
            res = subprocess.run(cmd, capture_output=True)
            print(res.stdout.decode('utf-8', errors='ignore'))
            if res.returncode != 0:
                print("Error:")
                print(res.stderr.decode('utf-8', errors='ignore'))
        except Exception as e:
            print(f"Failed to execute: {e}")

if __name__ == "__main__":
    main()
