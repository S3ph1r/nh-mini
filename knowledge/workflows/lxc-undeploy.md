# LXC Undeploy Workflow

## Overview

This document describes the complete LXC container undeployment workflow using the NH automation system.

## Components

### 1. Undeploy Script (`scripts/undeploy_lxc.py`)
- **Location**: `/home/Projects/NH-Mini/scripts/undeploy_lxc.py`
- **Purpose**: Handles complete container undeployment with cleanup
- **Security**: Uses SOPS+Age for credential management
- **Confirmation**: Requires user confirmation for destructive actions

### 2. Undeploy Skill Configuration
- **Location**: `/home/Projects/NH-Mini/.trae/skills/lxc-undeploy/SKILL.md`
- **Purpose**: Defines agent behavior and trigger patterns

## Workflow Steps

### Phase 1: Request Detection
The agent analyzes user input to detect undeploy requests using regex patterns:

```python
# Supported trigger patterns:
- "elimina lxc 197"
- "rimuovi container 198" 
- "distruggi ct199"
- "undeploy lxc 200"
- "elimina ct201"
```

### Phase 2: Pre-Validation
1. **Container Existence Check**: Verifies container exists before proceeding
2. **Status Reporting**: Shows current container state

### Phase 3: SSH Key Cleanup
1. **Key Identification**: Locates SSH key by comment pattern `nh-ct{vmid}@proxmox`
2. **Key Removal**: Executes: `sed -i '/nh-ct{vmid}@proxmox/d' /root/.ssh/authorized_keys`
3. **Verification**: Confirms key removal success

### Phase 4: Container Destruction
1. **Container Stop**: Stops running container with `pct stop {vmid}`
2. **Container Destroy**: Permanently removes container with `pct destroy {vmid}`
3. **Storage Cleanup**: Automatically removes associated storage volumes

### Phase 5: Inventory Update
1. **JSON Parsing**: Reads current inventory from `state/inventory.json`
2. **Entry Removal**: Removes container entry by VMID
3. **File Update**: Saves updated inventory

## Usage Examples

### Command Line Usage
```bash
# Basic undeploy
python3 scripts/undeploy_lxc.py 197
python3 scripts/undeploy_lxc.py 198
python3 scripts/undeploy_lxc.py 199
python3 scripts/undeploy_lxc.py 200
```

### Expected Output
```
🎯 **NH LXC Undeploy Summary**
**Container:** CT197
**Confidence:** 0.9

Proceed with undeployment? (y/N): y
🎯 Starting undeploy of CT197
==================================================
🔍 Checking if CT197 exists...
🔍 SSH Command: sshpass -p 'patatina' ssh root@192.168.1.2 "pct list | grep '^197\s'"
✅ CT197 found: 197        running                 ct197
🔑 Removing SSH key for CT197...
✅ SSH key removed for CT197
🛑 Stopping CT197...
✅ CT197 stopped successfully
💥 Destroying CT197...
✅ CT197 destroyed successfully
📋 Updating inventory...
✅ Removed CT197 from inventory
==================================================
🎉 CT197 undeployed successfully!
```

## Error Handling

### Container Not Found
- Agent detects non-existent containers
- Provides clear error messaging
- Prevents execution of subsequent steps

### SSH Key Issues
- Handles missing keys gracefully
- Continues with container destruction
- Logs warnings for manual cleanup if needed

### Container Stop Failures
- Detects already-stopped containers
- Proceeds with destruction step
- Provides appropriate status messages

### Inventory Update Issues
- Handles missing inventory files
- Validates JSON structure
- Reports update status

## Security Considerations

1. **SSH Key Cleanup**: Ensures no orphaned keys remain in authorized_keys
2. **Container Verification**: Prevents accidental destruction of wrong containers
3. **Confirmation Prompt**: Requires explicit user confirmation before destruction
4. **Logging**: Maintains audit trail of all undeploy operations

## Integration Points

### With Deploy Agent
- Complements `agent_lxc_handler.py` for full lifecycle management
- Uses same configuration and connection parameters
- Maintains consistent logging and error handling

### With Inventory System
- Updates same inventory.json file used by deploy agent
- Maintains data consistency across operations
- Preserves inventory structure and metadata

### With Proxmox Integration
- Uses standard `pct` commands for all operations
- Leverages existing SSH connection infrastructure
- Follows Proxmox best practices for container management

## Future Enhancements

- [ ] Bulk undeploy operations
- [ ] Automated cleanup scheduling
- [ ] Integration with monitoring systems
- [ ] Advanced filtering and selection criteria
- [ ] Rollback capabilities for emergency recovery