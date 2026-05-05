# ARIA Development Strategy: Runtime-First (PC 139 Primary)

> [!IMPORTANT]
> **ARIA** is a Windows-native system (PC 139) that interacts directly with NVIDIA GPUs and Windows file structures. 
> To avoid environment drift and "Double Maintenance" issues, follow this strategy:

## 1. Authoritative Source of Truth
- **PC 139 (192.168.1.139)** is the **PRIMARY** development and testing environment for ARIA.
- **LXC 190** (Dev) is a **SECONDARY** repository hub used primarily for viewing and documentation.

## 2. Development Workflow (Standard Rules)
1. **Modify on PC 139**: Always edit ARIA code directly on the production node via SSH or remote tools.
2. **Test on PC 139**: Verify all changes in the real runtime environment.
3. **Commit/Push from PC 139**: After successful tests, execute `git commit` and `git push` directly from the PC 139 terminal.
4. **Sync to Dev**: Perform `git pull` on LXC 190 to keep the central repository updated.

## 3. Directory Structure (PC 139)
- `C:\Users\Roberto\aria\aria_node_controller\`: Python Source Code.
- `C:\Users\Roberto\aria\data\assets\`: Standard Assets (v1.0) - Models & Voices.
- `C:\Users\Roberto\aria\data\outputs\`: Generated audio files.

## 4. Warnings for Future Agents
- **DO NOT** make architectural fixes on LXC 190 and push them to 139 without testing on the real target.
- **DO NOT** assume Linux paths (e.g., `/mnt/data`) work on ARIA. Always use Windows-style paths or `pathlib`.
- **ENCODING**: Always use **UTF-8 without BOM** when writing files to PC 139 via PowerShell.

---
*Created on 2026-03-26 to finalize ARIA v1.0 Activation.*
