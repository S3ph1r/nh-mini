import redis
import json

def main():
    r = redis.Redis(host='192.168.1.120', port=6379, db=0)
    try:
        keys = r.keys("*")
        result = {}
        target_substrings = ["aria", "qwen", "lifelog", "queue", "q:"]
        for key in keys:
            k_str = key.decode('utf-8', errors='ignore')
            if not any(sub in k_str.lower() for sub in target_substrings):
                continue
            try:
                k_type = r.type(key).decode('utf-8')
                
                if k_type == 'list':
                    val = r.llen(key)
                elif k_type == 'set':
                    val = r.scard(key)
                elif k_type == 'zset':
                    val = r.zcard(key)
                elif k_type == 'hash':
                    val = r.hlen(key)
                elif k_type == 'string':
                    # Only show length of string or short string to avoid clutter
                    s_val = r.get(key)
                    val = f"string (len={len(s_val)})" if s_val else "None"
                elif k_type == 'stream':
                    val = r.xlen(key)
                else:
                    val = "unknown data type"
            except Exception as inner_e:
                k_type = "error"
                val = str(inner_e)
            
            result[k_str] = {
                "type": k_type,
                "length_or_val": val
            }
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error connecting to Redis: {e}")

if __name__ == "__main__":
    main()
