#!/usr/bin/env python3
"""
Production Manager — one-click GitHub Pages deployment
Run:  python3 deploy.py
  or: python3 deploy.py YOUR_TOKEN_HERE
"""
import urllib.request, urllib.error, json, base64, os, sys, re

API = "https://api.github.com"
REPO_NAME = "production-manager"
FILE = "index.html"

def api(method, path, data=None, token=""):
    url = API + path
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def clean_token(raw):
    return re.sub(r'\s+', '', raw).strip()

def main():
    print("\n🏭 Production Manager — GitHub Pages Deployer")
    print("=" * 45)

    # Token resolution: CLI arg → GH_DEPLOY_TOKEN env → .deploy_token file → prompt
    token = ""
    token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".deploy_token")
    if len(sys.argv) > 1:
        token = clean_token(sys.argv[1])
        print(f"✓ Using token from command line (ends: …{token[-4:]})")
    elif os.environ.get("GH_DEPLOY_TOKEN"):
        token = clean_token(os.environ["GH_DEPLOY_TOKEN"])
        print(f"✓ Using token from GH_DEPLOY_TOKEN env var (ends: …{token[-4:]})")
    elif os.path.exists(token_file):
        with open(token_file) as f:
            token = clean_token(f.read())
        print(f"✓ Using token from .deploy_token file (ends: …{token[-4:]})")
    else:
        print("\nYou need a GitHub Personal Access Token with the 'repo' scope")
        print("(add 'gist' too for in-app cloud sync).")
        print("Create one at: https://github.com/settings/tokens/new\n")
        print("TIP: save it once so you never have to paste it again:")
        print('     echo "ghp_yourTokenHere" > .deploy_token\n')
        token = clean_token(input("Paste your token here and press Enter: "))

    if not token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)

    user_data, status = api("GET", "/user", token=token)
    if status != 200:
        print(f"❌ Invalid token or auth error: {user_data.get('message')}")
        sys.exit(1)
    username = user_data["login"]
    print(f"✓ Authenticated as: {username}")

    repo_data, status = api("GET", f"/repos/{username}/{REPO_NAME}", token=token)
    if status == 404:
        print(f"Creating repository '{REPO_NAME}'...")
        repo_data, status = api("POST", "/user/repos", {
            "name": REPO_NAME,
            "description": "Production Manager — Manufacturing & WIP Tracking",
            "private": False,
            "auto_init": False
        }, token=token)
        if status not in (200, 201):
            print(f"❌ Failed to create repo: {repo_data.get('message')}")
            sys.exit(1)
        print(f"✓ Repository created: {repo_data['html_url']}")
    else:
        print(f"✓ Repository exists: {repo_data['html_url']}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, FILE)
    if not os.path.exists(html_path):
        print(f"❌ {FILE} not found in {script_dir}")
        sys.exit(1)

    with open(html_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    file_data, status = api("GET", f"/repos/{username}/{REPO_NAME}/contents/{FILE}", token=token)
    sha = file_data.get("sha") if status == 200 else None

    print(f"{'Updating' if sha else 'Uploading'} {FILE}...")
    payload = {"message": "Deploy Production Manager", "content": content_b64, "branch": "main"}
    if sha:
        payload["sha"] = sha

    _, status = api("PUT", f"/repos/{username}/{REPO_NAME}/contents/{FILE}", payload, token=token)
    if status not in (200, 201):
        print(f"❌ Failed to upload file")
        sys.exit(1)
    print(f"✓ {FILE} deployed")

    pages_data, status = api("GET", f"/repos/{username}/{REPO_NAME}/pages", token=token)
    if status == 404:
        print("Enabling GitHub Pages...")
        _, status = api("POST", f"/repos/{username}/{REPO_NAME}/pages", {
            "source": {"branch": "main", "path": "/"}
        }, token=token)
        if status in (200, 201, 204):
            print("✓ GitHub Pages enabled")
        else:
            print("⚠ Could not auto-enable Pages — enable it manually:")
            print(f"  https://github.com/{username}/{REPO_NAME}/settings/pages  (Branch=main, folder=/)")
    else:
        print(f"✓ GitHub Pages already active")

    pages_url = f"https://{username}.github.io/{REPO_NAME}/"
    print(f"\n{'='*45}")
    print(f"🌐 Your app is live at:\n   {pages_url}")
    print(f"\n⏱  It may take 1–2 minutes for GitHub Pages to go live.")
    print(f"\n🔗 To link with Export Manager:")
    print(f"   1. Open Production Manager → Settings → Cloud Sync")
    print(f"   2. Paste the SAME token + Gist ID you use in Export Manager")
    print(f"   3. Click 'Import Orders from Export Manager'\n")

if __name__ == "__main__":
    main()
