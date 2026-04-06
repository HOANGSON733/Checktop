"""
Lưu và tải trạng thái phiên làm việc
"""

import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd


# ===================== SAVE SESSION STATE =====================
def save_session_state():
    """Lưu session state vào file JSON"""
    user_id = st.session_state.get('user_id', 'default')
    session_file = f"dashboard_session_{user_id}.json"
    session_data = {
        'user_id': st.session_state.get('user_id'),
        'user_sheets_config': st.session_state.get('user_sheets_config', []),
        'selected_domain': st.session_state.get('selected_domain', ''),
        'goals': {},
        'snapshots': {},
        'saved_filters': st.session_state.get('saved_filters', {}),
        'theme': st.session_state.get('theme', 'dark'),
        'notes': st.session_state.get('notes', {}),
        'display_name': st.session_state.get('display_name', ''),
        'avatar': st.session_state.get('avatar', None),
    }
    
    # Convert goals (which may contain date objects) into serializable form
    for goal_id, goal in st.session_state.get('goals', {}).items():
        goal_serial = goal.copy()
        if 'deadline' in goal_serial and isinstance(goal_serial['deadline'], date):
            goal_serial['deadline'] = goal_serial['deadline'].isoformat()
        if 'created' in goal_serial and isinstance(goal_serial['created'], datetime):
            goal_serial['created'] = goal_serial['created'].isoformat()
        session_data['goals'][goal_id] = goal_serial
    
    # Convert snapshots (which may contain DataFrames) into serializable form
    for name, snap in st.session_state.get('snapshots', {}).items():
        snap_serial = {}
        
        # Date -> ISO string
        date_val = snap.get('date')
        if isinstance(date_val, datetime):
            snap_serial['date'] = date_val.isoformat()
        elif isinstance(date_val, date):
            snap_serial['date'] = date_val.isoformat()
        else:
            snap_serial['date'] = str(date_val)
        
        snap_serial['score'] = snap.get('score')
        snap_serial['note'] = snap.get('note', '')
        
        data_val = snap.get('data')
        # If data is a DataFrame, convert to list of records
        if isinstance(data_val, pd.DataFrame):
            try:
                # Convert datetime columns to strings to make JSON serializable
                data_copy = data_val.copy()
                for col in data_copy.columns:
                    if pd.api.types.is_datetime64_any_dtype(data_copy[col]):
                        data_copy[col] = data_copy[col].astype(str)
                snap_serial['data'] = data_copy.to_dict(orient='records')
            except Exception:
                snap_serial['data'] = []
        elif isinstance(data_val, list):
            snap_serial['data'] = data_val
        else:
            # Fallback: stringify
            snap_serial['data'] = str(data_val)
        
        session_data['snapshots'][name] = snap_serial
    
    # Also save default bridge file
    default_data = {
        'user_id': st.session_state.get('user_id'),
        'user_sheets_config': st.session_state.get('user_sheets_config', [])
    }
    with open('dashboard_session_default.json', 'w', encoding='utf-8') as f:
        json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    try:
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"❌ Lỗi khi lưu session: {e}")


# ===================== LOAD SESSION STATE =====================
def load_session_state(restore_auth=True):
    """Tải session state từ file JSON. restore_auth=False skips auth restoration."""
    import pandas as pd
    # Try to load with default first, then restore user_id if valid
    session_file = "dashboard_session_default.json"
    saved_user_id = None
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                saved_user_id = data.get('user_id')
                # 🔒 Validate: if current user_id exists, only load matching session
                current_user_id = st.session_state.get('user_id')
                if current_user_id and saved_user_id != current_user_id:
                    st.session_state.avatar = None  # Clear stale
                    return data  # Load default data but no avatar
                
                if saved_user_id and restore_auth:
                    # Load full session for this user
                    user_session_file = f"dashboard_session_{saved_user_id}.json"
                    if os.path.exists(user_session_file):
                        with open(user_session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                            return session_data
                    else:
                        session_data = data
                        return session_data
                else:
                    session_data = data
                    return session_data
        except Exception as e:
            st.warning(f"⚠️ Không thể tải session default: {e}")
            return {}
    else:
        return {}
    
    # ONLY restore auth if explicitly allowed
    if restore_auth and saved_user_id and 'user_id' not in st.session_state:
        st.session_state.user_id = saved_user_id
        st.session_state.user_sheets_config = session_data.get('user_sheets_config', [])

    
    # Convert string dates back to datetime objects for other data (always)
    if 'goals' in session_data:
        for goal_id, goal in session_data['goals'].items():
            if 'deadline' in goal and isinstance(goal['deadline'], str):
                try:
                    goal['deadline'] = datetime.fromisoformat(goal['deadline']).date()
                except Exception:
                    pass
            if 'created' in goal and isinstance(goal['created'], str):
                try:
                    goal['created'] = datetime.fromisoformat(goal['created'])
                except Exception:
                    pass
    
    if 'snapshots' in session_data:
        for snap_name, snap_data in session_data['snapshots'].items():
            # Convert date string back to datetime
            if 'date' in snap_data and isinstance(snap_data['date'], str):
                try:
                    snap_data['date'] = datetime.fromisoformat(snap_data['date'])
                except Exception:
                    try:
                        snap_data['date'] = datetime.fromisoformat(snap_data['date'].replace(' ', 'T'))
                    except Exception:
                        try:
                            snap_data['date'] = datetime.fromisoformat(snap_data['date']).replace(
                                hour=0, minute=0, second=0, microsecond=0
                            )
                        except Exception:
                            snap_data['date'] = datetime.now()
            
            # Convert stored data (list of records) back to DataFrame
            if 'data' in snap_data and isinstance(snap_data['data'], list):
                try:
                    snap_data['data'] = pd.DataFrame(snap_data['data'])
                except Exception:
                    pass
    
    return session_data

def load_app_data_only():
    """Load app data (goals/snapshots) WITHOUT restoring auth state"""
    return load_session_state(restore_auth=False)


# ===================== INITIALIZE SESSION STATE =====================
def clear_all_session_files():
    """Clear ALL session files on logout - enhanced"""
    import glob
    # Delete all dashboard_session_*.json files
    session_files = glob.glob("dashboard_session_*.json")
    session_files.append("dashboard_session_default.json")
    for f in session_files:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"Deleted {f}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")

def init_session_state(restore_auth=True):
    """Khởi tạo session state. restore_auth=True only after login confirmed."""
    # Always initialize avatar safely first
    if 'avatar' not in st.session_state:
        st.session_state.avatar = None
    elif restore_auth and st.session_state.get('user_id'):
        saved_session = load_session_state(restore_auth=restore_auth)
        # 🔒 CRITICAL: Validate user_id before restoring avatar
        saved_user_id = saved_session.get('user_id')
        if saved_user_id != st.session_state.user_id:
            st.warning("⚠️ Session mismatch - clearing stale avatar")
            st.session_state.avatar = None
            st.rerun()
        else:
            st.session_state.avatar = saved_session.get('avatar', None)
    else:
        # No auth or explicit clear
        st.session_state.avatar = None
    
    saved_session = load_session_state(restore_auth=restore_auth)
    
    # Initialize app data (safe always)
    if 'goals' not in st.session_state:
        st.session_state.goals = saved_session.get('goals', {})
    if 'snapshots' not in st.session_state:
        st.session_state.snapshots = saved_session.get('snapshots', {})
    if 'saved_filters' not in st.session_state:
        st.session_state.saved_filters = saved_session.get('saved_filters', {})
    if 'selected_domain' not in st.session_state:
        st.session_state.selected_domain = saved_session.get('selected_domain', '')
    if 'theme' not in st.session_state:
        st.session_state.theme = saved_session.get('theme', 'dark').lower()
    if 'notes' not in st.session_state:
        st.session_state.notes = saved_session.get('notes', {})
    if 'display_name' not in st.session_state:
        st.session_state.display_name = saved_session.get('display_name', st.session_state.get('user_id', ''))

