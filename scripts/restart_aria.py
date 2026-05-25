import subprocess
import time

def main():
    print("Initiating full ARIA restart on PC 139...")
    
    # 1. Kill python and llama-server processes
    kill_cmds = [
        ["ssh", "roberto@192.168.1.139", "taskkill /F /IM python.exe /T"],
        ["ssh", "roberto@192.168.1.139", "taskkill /F /IM python3.exe /T"],
        ["ssh", "roberto@192.168.1.139", "taskkill /F /IM llama-server.exe /T"]
    ]
    
    for cmd in kill_cmds:
        print(f"Running: {' '.join(cmd)}")
        res = subprocess.run(cmd, capture_output=True)
        # We don't crash if processes aren't running
        print(res.stdout.decode('utf-8', errors='ignore'))
        
    print("Waiting 3 seconds for GPU memory to clear...")
    time.sleep(3)
    
    # 2. Launch aria.bat via cmd /c
    launch_cmd = [
        "ssh", "roberto@192.168.1.139",
        "cmd.exe /c C:\\Users\\Roberto\\aria\\aria.bat"
    ]
    print(f"Running: {' '.join(launch_cmd)}")
    res = subprocess.run(launch_cmd, capture_output=True)
    print(res.stdout.decode('utf-8', errors='ignore'))
    if res.returncode == 0:
        print("ARIA restart command executed successfully!")
    else:
        print("Error launching ARIA:")
        print(res.stderr.decode('utf-8', errors='ignore'))

if __name__ == "__main__":
    main()
