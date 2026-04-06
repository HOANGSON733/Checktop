import os
import shutil
import time
from pathlib import Path
import argparse

def cleanup_profiles(hours_old=24, dry_run=False):
    """Cleanup old Chrome profiles in TSEO_Profiles"""
    app_data = os.getenv('LOCALAPPDATA', str(Path.home()))
    profiles_dir = Path(app_data) / 'TSEO_Profiles'
    
    if not profiles_dir.exists():
        print("✅ No TSEO_Profiles directory found (clean)")
        return
    
    print(f"🔍 Scanning: {profiles_dir}")
    
    deleted = 0
    total_size = 0
    
    for profile_dir in profiles_dir.glob('Profile_*'):
        try:
            # Get modification time
            mod_time = profile_dir.stat().st_mtime
            age_hours = (time.time() - mod_time) / 3600
            
            if age_hours > hours_old:
                size = sum(f.stat().st_size for f in profile_dir.rglob('*') if f.is_file())
                
                if dry_run:
                    print(f"🧹 DRY-RUN: {profile_dir.name} ({age_hours:.1f}h old, {size/1024/1024:.1f}MB)")
                else:
                    shutil.rmtree(profile_dir)
                    print(f"🗑️  DELETED: {profile_dir.name} ({age_hours:.1f}h old, {size/1024/1024:.1f}MB)")
                    deleted += 1
                    total_size += size
        except Exception as e:
            print(f"⚠️  Skip {profile_dir}: {e}")
    
    if dry_run:
        print("\n✅ DRY-RUN complete - No files deleted")
    else:
        print(f"\n✅ Cleanup complete: {deleted} profiles, {total_size/1024/1024:.1f}MB freed")
    
    print(f"📁 Final state: {len(list(profiles_dir.glob('Profile_*'))) if profiles_dir.exists() else 0} profiles left")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cleanup Chrome Profiles')
    parser.add_argument('--hours', type=int, default=24, help='Delete profiles older than N hours')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted')
    args = parser.parse_args()
    
    cleanup_profiles(args.hours, args.dry_run)

