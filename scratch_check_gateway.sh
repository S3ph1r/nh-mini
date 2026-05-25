#!/bin/bash
ssh -o StrictHostKeyChecking=no root@192.168.1.202 "ps aux | grep -E 'nginx|ngrok'; echo '---'; tail -n 25 /var/log/nginx/gateway_access.log"
