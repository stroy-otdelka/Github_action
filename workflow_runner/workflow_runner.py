#! /usr/bin/env python3

import json
import time
import argparse
from pprint import pprint

import requests


def run_workflow(token: str, name: str, branch: str):
    url = f"https://api.github.com/repos/stroy-otdelka/Stroy-Otdelka-System/actions/workflows/{name}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {"ref": branch}
    response = requests.post(url, headers=headers, json=data)
    if response.text and response.json()["message"] in ("Not Found", "Bad credentials"):
        raise ValueError("Были переданы неверные данные!")
    print(f"workflow {name} запущено")


def get_workflow_info(token: str, name: str, branch: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {"ref": branch}

    info_url = f"https://api.github.com/repos/stroy-otdelka/Stroy-Otdelka-System/actions/workflows/{name}"

    info_response = requests.get(info_url, headers=headers, json=data)

    workflow_id = info_response.json()["id"]

    state_url = f"https://api.github.com/repos/stroy-otdelka/Stroy-Otdelka-System/actions/runs"
    response = requests.get(state_url, headers=headers, json=data)
    workflow = [x for x in response.json()["workflow_runs"] if x["workflow_id"] == workflow_id][0]
    return workflow['conclusion']


def wait_workflow(token: str, name: str, branch: str):
    run_workflow(token, name, branch)
    print(f"workflow {name} выполняется...")
    conclusion = None
    while not conclusion:
        time.sleep(5)
        conclusion = get_workflow_info(token, name, branch)
    return conclusion


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="run workflows")
    parser.add_argument("token", type=str, help="github token")
    parser.add_argument("workflow_name", type=str, help="workflow name")
    parser.add_argument("branch", type=str, help="branch where locate workflow")

    args = parser.parse_args()

    conclusion_res = wait_workflow(args.token, args.workflow_name, args.branch)
    if conclusion_res == "success":
        print(f"workflow {args.workflow_name} завершило свою работу успешно")
    else:
        raise RuntimeError(f"workflow {args.workflow_name} завершило свою работу с conclusion = {conclusion_res}")
