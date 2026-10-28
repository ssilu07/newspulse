"""
Prune old Vercel deployments to keep storage usage well under the 10 GB Hobby limit.
Works seamlessly locally (using local Vercel OAuth) or in CI/CD (via VERCEL_TOKEN env var).
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

PROJECTS = {
    "techpulse": "prj_7VLjJhCzu4JJWhNkTqhsxE7xwEGz",
    "newspulse-oq75": "prj_rFnl2sQMTNLFGgeS9R9Pdz8HBDlk",
    "cinestories": "prj_yUQofgAJM96b5n6F2v3Cf41Jp5Da"
}

def get_token():
    # 1. Check environment variable
    token = os.environ.get("VERCEL_TOKEN")
    if token:
        return token
        
    # 2. Check local Antigravity MCP token file
    home = os.path.expanduser("~")
    token_file = os.path.join(home, ".gemini", "antigravity", "mcp_oauth_tokens.json")
    if os.path.isfile(token_file):
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d.get("https://mcp.vercel.com", {}).get("token", {}).get("access_token")
        except Exception:
            pass
    return None

def fetch_deployments(token, project_id):
    url = f"https://api.vercel.com/v6/deployments?projectId={project_id}&limit=100"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data.get("deployments", [])
    except Exception as e:
        print(f"Error fetching deployments for project {project_id}: {e}")
        return []

def delete_deployment(token, dep_id):
    url = f"https://api.vercel.com/v13/deployments/{dep_id}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print(f"Failed to delete {dep_id}: HTTP {e.code}")
        return False
    except Exception as e:
        print(f"Failed to delete {dep_id}: {e}")
        return False

def prune_project(token, name, project_id, keep_count=3):
    deps = fetch_deployments(token, project_id)
    if not deps:
        print(f"[{name}] No deployments found.")
        return 0
        
    deps_sorted = sorted(deps, key=lambda x: x.get('created', 0), reverse=True)
    to_keep = deps_sorted[:keep_count]
    to_delete = deps_sorted[keep_count:]
    
    print(f"[{name}] Total: {len(deps_sorted)}. Keeping latest {len(to_keep)}, deleting {len(to_delete)} old.")
    
    deleted = 0
    for dep in to_delete:
        dep_id = dep.get("uid")
        if delete_deployment(token, dep_id):
            deleted += 1
            print(f"  [{name}] Deleted old deployment: {dep_id}")
        time.sleep(0.15)
    return deleted

def main():
    token = get_token()
    if not token:
        print("Notice: VERCEL_TOKEN not set and local token not found. Skipping Vercel prune.")
        return 0
        
    keep = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print(f"Starting Vercel deployment pruning (keeping {keep} latest per project)...")
    
    total = 0
    for name, pid in PROJECTS.items():
        total += prune_project(token, name, pid, keep_count=keep)
        
    print(f"Prune complete. Successfully removed {total} obsolete deployment(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
