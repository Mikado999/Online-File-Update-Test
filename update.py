import requests
import json
from base64 import b64encode, b64decode
import re
import sys

# ================= Configuration =================
TOKEN = "YOUR_PERSONAL_ACCESS_TOKEN"  # GitHub token
REPO = "username/repo"                 # GitHub repo
FILE_PATH = "single_data.py"           # The script file in the repo
BRANCH = "main"
API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
# =================================================

# ==================== Read internal data ====================
# The data is stored between the markers: #<<DATA>> ... #<<ENDDATA>>
def read_internal_data():
    with open(sys.argv[0], "r", encoding="utf-8") as f:
        code = f.read()
    match = re.search(r"#<<DATA>>\n(.*?)\n#<<ENDDATA>>", code, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    else:
        return {"counter": 0}  # default if no data found

# ==================== Write internal data ===================
def write_internal_data(data):
    with open(sys.argv[0], "r", encoding="utf-8") as f:
        code = f.read()
    new_data_str = json.dumps(data, indent=4)
    if "#<<DATA>>" in code:
        code = re.sub(r"#<<DATA>>\n(.*?)\n#<<ENDDATA>>",
                      f"#<<DATA>>\n{new_data_str}\n#<<ENDDATA>>", code, flags=re.DOTALL)
    else:
        # Add data section if not present
        code += f"\n#<<DATA>>\n{new_data_str}\n#<<ENDDATA>>\n"
    with open(sys.argv[0], "w", encoding="utf-8") as f:
        f.write(code)

# ==================== GitHub Sync ====================
def push_to_github(data):
    # Get current SHA
    r = requests.get(API_URL, headers={"Authorization": f"token {TOKEN}"})
    if r.status_code == 200:
        sha = r.json()["sha"]
    else:
        sha = None

    content = b64encode(open(sys.argv[0], "rb").read()).decode()
    payload = {
        "message": "Update internal data",
        "content": content,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(API_URL, headers={"Authorization": f"token {TOKEN}"}, json=payload)
    if r.status_code in [200, 201]:
        print("GitHub sync successful!")
    else:
        print("GitHub sync failed:", r.status_code, r.text)

# ==================== Main Logic ====================
data = read_internal_data()
data["counter"] += 1
print("Current counter:", data["counter"])
write_internal_data(data)
push_to_github(data)

#<<DATA>>
{
    "counter": 0
}
#<<ENDDATA>>
