import subprocess

def main():
    cmds = [
        ["ssh", "roberto@192.168.1.139", "whoami"],
        ["ssh", "roberto@192.168.1.139", "powershell -Command \"Get-ChildItem C:\\Users\""]
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
