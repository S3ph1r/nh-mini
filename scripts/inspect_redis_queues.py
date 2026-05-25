import redis
import json

def main():
    r = redis.Redis(host='192.168.1.120', port=6379, db=0)
    try:
        keys = r.keys("*")
        result = {}
        for key in keys:
            k_str = key.decode('utf-8', errors='ignore')
            k_type = r.type(key).decode('utf-8')
            
            if k_type in ['list', 'stream', 'set', 'zset', 'hash']:
                if k_type == 'list':
                    val = r.llen(key)
                elif k_type == 'stream':
                    val = r.xlen(key)
                elif k_type == 'set':
                    val = r.scard(key)
                elif k_type == 'zset':
                    val = r.zcard(key)
                elif k_type == 'hash':
                    val = r.hlen(key)
                
                result[k_str] = {
                    "type": k_type,
                    "length": val
                }
        # print sorted by name
        for k in sorted(result.keys()):
            print(f"{k} ({result[k]['type']}): {result[k]['length']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
