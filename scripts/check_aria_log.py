import subprocess

def main():
    cmd = [
        "ssh", "roberto@192.168.1.139",
        "powershell -Command \"Get-Content C:\\Users\\Roberto\\aria\\logs\\aria_orchestrator.log -Tail 30\""
    ]
    try:
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0:
            print(res.stdout.decode('utf-8', errors='ignore'))
        else:
            print(f"Error (code {res.returncode}):")
            print(res.stderr.decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"Failed to execute: {e}")

if __name__ == "__main__":
    main()
