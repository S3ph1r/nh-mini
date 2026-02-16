---
name: "lxc-undeploy"
description: "Handles LXC container undeployment including SSH key cleanup, container destruction, and inventory updates. Invoke when user asks to remove/delete/destroy LXC containers."
---

# LXC Undeploy Agent

This skill manages the complete undeployment workflow for LXC containers with proper cleanup.

## Workflow

1. **SSH Key Removal**: Removes container's SSH key from Proxmox authorized_keys
2. **Container Destruction**: Stops and destroys the LXC container
3. **Inventory Update**: Removes container entry from inventory.json

## Usage Examples

- "elimina lxc 195"
- "rimuovi container 196" 
- "distruggi ct197"
- "undeploy lxc 198"

## Implementation

The agent should:
1. Parse VMID from user input using regex
2. Remove SSH key: `sed -i '/nh-ct{vmid}@proxmox/d' /root/.ssh/authorized_keys`
3. Stop container: `pct stop {vmid}`
4. Destroy container: `pct destroy {vmid}`
5. Update inventory.json removing the container entry
6. Provide detailed logging of each step

## Error Handling

- Check if container exists before attempting removal
- Handle cases where container is already stopped
- Verify SSH key removal success
- Validate inventory updates