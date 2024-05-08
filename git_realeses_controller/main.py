from os import path, mkdir
import shutil

import variables
import requests
from pathlib import Path

parent_dir = path.dirname(path.abspath(__file__))
static_path = Path(f"{parent_dir}/../static")
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"Bearer {variables.GITHUB_TOKEN}"
}


def get_last_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    release = requests.get(url, headers=headers)

    if release.status_code != 200:
        return None

    release = release.json()

    data = {
        "id": release["id"],
        "name": release["name"],
        "body": release["body"],
        "assets": []
    }

    assets_url = release["assets_url"]
    assets = requests.get(assets_url, headers=headers).json()

    for asset in assets:
        data["assets"].append({
            "url": asset["url"],
            "name": asset["name"],
        })

    return data


def download_files(name, assets):
    headers_download = headers.copy()
    headers_download["Accept"] = "application/octet-stream"
    dir_path = f"{static_path}/{name}"

    if path.exists(dir_path):
        shutil.rmtree(dir_path)

    mkdir(dir_path)

    for asset in assets:
        asset_binary = requests.get(asset["url"], headers=headers_download)
        with open(f"{dir_path}/{asset['name']}", "wb") as f:
            f.write(asset_binary.content)


if __name__ == '__main__':
    a = get_last_release('Playtronica', 'biotron-firmware')
    download_files("test", a["assets"])
