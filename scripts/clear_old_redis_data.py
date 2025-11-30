"""
Utility script to clear old Redis data from previous days.
This keeps Redis clean by removing data that's no longer needed.
"""

import redis
import sys
from datetime import datetime, timedelta


def clear_old_data(days_to_keep=0, redis_host='localhost', redis_port=6379):
    """
    Clear Redis data older than the specified number of days.
    
    Args:
        days_to_keep: Number of days to keep (0 = only keep today's data)
        redis_host: Redis host
        redis_port: Redis port
    """
    try:
        # Connect to Redis
        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=5
        )
        client.ping()
        print(f"✓ Connected to Redis at {redis_host}:{redis_port}\n")
        
    except Exception as e:
        print(f"✗ Failed to connect to Redis: {e}")
        sys.exit(1)
    
    # Calculate cutoff date
    cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date()
    today = datetime.now().date().isoformat()
    
    print("=" * 80)
    print(f"Clearing Redis data older than: {cutoff_date.isoformat()}")
    print(f"Today's date: {today}")
    print("=" * 80 + "\n")
    
    # Get all highest_price keys
    all_keys = client.keys("highest_price:*")
    
    if not all_keys:
        print("No data found in Redis.")
        return
    
    print(f"Found {len(all_keys)} total keys\n")
    
    deleted_count = 0
    kept_count = 0
    
    for key in all_keys:
        # Extract date from key: highest_price:YYYY-MM-DD:SYMBOL
        parts = key.split(':')
        if len(parts) >= 3:
            key_date_str = parts[1]
            
            try:
                key_date = datetime.fromisoformat(key_date_str).date()
                
                if key_date < cutoff_date:
                    client.delete(key)
                    deleted_count += 1
                    print(f"🗑️  Deleted: {key} (date: {key_date_str})")
                else:
                    kept_count += 1
                    
            except ValueError:
                print(f"⚠️  Skipping invalid date in key: {key}")
    
    print("\n" + "=" * 80)
    print(f"✓ Cleanup complete!")
    print(f"  - Deleted: {deleted_count} keys")
    print(f"  - Kept: {kept_count} keys")
    print("=" * 80)


def clear_all_data(redis_host='localhost', redis_port=6379):
    """Clear ALL Redis data (use with caution!)"""
    try:
        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            socket_connect_timeout=5
        )
        client.ping()
        
        all_keys = client.keys("highest_price:*")
        if all_keys:
            client.delete(*all_keys)
            print(f"✓ Deleted all {len(all_keys)} keys")
        else:
            print("No data to delete")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clear old Redis data from TickerFlow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear all data except today's
  python scripts/clear_old_redis_data.py
  
  # Keep last 7 days of data
  python scripts/clear_old_redis_data.py --days-to-keep 7
  
  # Clear ALL data (use with caution!)
  python scripts/clear_old_redis_data.py --clear-all
        """
    )
    
    parser.add_argument(
        '--days-to-keep',
        type=int,
        default=0,
        help='Number of days to keep (default: 0, only keep today)'
    )
    
    parser.add_argument(
        '--clear-all',
        action='store_true',
        help='Clear ALL data (use with caution!)'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Redis host (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=6379,
        help='Redis port (default: 6379)'
    )
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║         TickerFlow Redis Data Cleanup Utility                ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    if args.clear_all:
        confirm = input("⚠️  Are you sure you want to delete ALL data? (yes/no): ")
        if confirm.lower() == 'yes':
            clear_all_data(args.host, args.port)
        else:
            print("Cancelled.")
    else:
        clear_old_data(args.days_to_keep, args.host, args.port)



