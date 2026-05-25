import redis

def main():
    r = redis.Redis(host='192.168.1.120', port=6379, db=0)
    try:
        # Find keys to delete
        patterns = [
            "aria:q:llm:local:qwen3-14b-q4km:lifelog",
            "aria:result:llm:*",
            "aria:result:imagegen:*",
            "gpu:queue:tts:qwen3-tts"
        ]
        
        deleted_count = 0
        for pattern in patterns:
            keys = r.keys(pattern)
            for key in keys:
                r.delete(key)
                print(f"Deleted key: {key.decode('utf-8')}")
                deleted_count += 1
        
        print(f"Cleanup finished! Deleted {deleted_count} stale queue/result keys from Redis.")
    except Exception as e:
        print(f"Error during Redis cleanup: {e}")

if __name__ == "__main__":
    main()
