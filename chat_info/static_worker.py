import asyncio
import json
from os import path
from pathlib import Path

import variables
from git_realeses_controller import *


parent_dir = path.dirname(path.abspath(__file__))
file_path = Path(f"{parent_dir}/../static/chats_info.json")
repo_path = Path(f"{parent_dir}/../repositories.json")


def check_repos():
    with open(file_path, "r") as cur_data:
        data: dict = json.load(cur_data)

    handler = {}
    for repo in data["repositories"]:
        last_release = get_last_release(data["repositories"][repo]["OWNER"], data["repositories"][repo]["REPO"])
        if not last_release:
            if data["repositories"][repo]["id"] > 0:
                data["repositories"][repo]["id"] = 0
            continue
        if last_release["id"] != data["repositories"][repo]["id"]:
            data["repositories"][repo]["id"] = last_release["id"]
            data["repositories"][repo]["name"] = last_release["name"]
            data["repositories"][repo]["body"] = last_release["body"]
            data["repositories"][repo]["assets"] = last_release["assets"][:]
            download_files(repo, last_release["assets"])
            handler[repo] = last_release

    with open(file_path, "w") as file:
        json.dump(data, file)

    return handler


def init():
    if not file_path.exists():
        initial_dct = {
            "chats": {},
            "repositories": {}
        }

        with open(file_path, "w+") as file:
            json.dump(initial_dct, file)

    with open(file_path, "r") as cur_data:
        data: dict = json.load(cur_data)

    with open(repo_path, "r") as linked_reps:
        linked_reps = json.load(linked_reps)

    for key in list(data["repositories"].keys()):
        if key not in linked_reps:
            data["repositories"].pop(key)

    for key in linked_reps:
        if key not in data["repositories"]:
            data["repositories"][key] = {
                'OWNER': "",
                'REPO': "",
                'id': 0,
                "name": "",
                "body": "",
                "assets": []
            }
        if (linked_reps[key]["OWNER"] != data["repositories"][key]["OWNER"]) or \
                (linked_reps[key]["REPO"] != data["repositories"][key]["REPO"]):
            data["repositories"][key]["OWNER"] = linked_reps[key]["OWNER"]
            data["repositories"][key]["REPO"] = linked_reps[key]["REPO"]
            data["repositories"][key]["id"] = 0

    with open(file_path, "w") as file:
        json.dump(data, file)



def check_chat_existance(chat_id: int):
    with open(file_path, "r") as cur_data:
        data: dict = json.load(cur_data)

    return str(chat_id) in data['chats']


def get_chat_with_topic(topic):
    with open(file_path, "r") as cur_data:
        data: dict = json.load(cur_data)

    res = []
    for chat_id in data["chats"]:
        if topic in set(data["chats"][chat_id]):
            res.append(chat_id)
    return res


def get_repos(chat_id):
    with open(file_path, "r") as cur_data:
        data: dict = json.load(cur_data)

    if str(chat_id) in data["chats"]:
        return set(data["chats"][str(chat_id)]), set(data["repositories"].keys())
    else:
        return set(), set(data["repositories"].keys())


def set_chat(chat_id: int, repo: str):
    with open(file_path, "r") as cur_data:
        data: dict = json.load(cur_data)

    if str(chat_id) not in data["chats"]:
        data["chats"][str(chat_id)] = []
    data["chats"][str(chat_id)].append(repo)

    with open(file_path, "w") as file:
        json.dump(data, file)


def delete_chat(chat_id: int, repo: str):
    with open(file_path, "r") as cur_data:
        data: dict = json.load(cur_data)

    data["chats"][str(chat_id)].remove(repo)

    with open(file_path, "w") as file:
        json.dump(data, file)


if __name__ == '__main__':
    file_path = Path("../static/chats_info.json")
    repo_path = Path("../repositories.json")
    init()
