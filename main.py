from pywinusb import hid
import requests
from datetime import datetime, timezone
import os
import time
import json
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum
from http import HTTPStatus
import sys
import pprint

class Action(Enum):
    START_PROJ = "START_PROJ"
    STOP_ANY   = "STOP_ANY"    

@dataclass
class ButtonAction:
    description : str
    project_id  : str
    task_id     : str
    text        : Optional[str]

@dataclass
class ClockifyConfig:
    api_key      : str
    workspace_id : str

@dataclass
class ClockifyTask:
    id   : str
    name : str

@dataclass
class ClockifyProject:
    id   : str
    name : str
    tasks : list[ClockifyTask]

#    project_id   : Optional[str]
#    buttons      : Optional[dict[int, str]]

def read_config(config_file_path):
    with open(config_file_path, "r") as f:
         data = json.load(f)
    return ClockifyConfig(**data)




class Clockify:
    BASE_URL = "https://api.clockify.me/api/v1"

    def __init__(self, config: ClockifyConfig):
        self._config      = config

    def get_projects(self):
        projects_list = []
        page = 0
        while True:
            page += 1 
            
            url = f'https://api.clockify.me/api/v1/workspaces/{self._config.workspace_id}/projects?page={page}&page-size=5000&archived=false'            
            response = requests.get(url, headers={'X-Api-Key': self._config.api_key})

            if response.status_code == HTTPStatus.OK:
                projects_this_page = response.json()
                if (len(projects_this_page) > 0):
                    projects_list.extend([ClockifyProject(id=project['id'], name=project['name'], tasks=self._get_project_tasks(project['id'])) for project in projects_this_page])
                else:
                    break
            else:
                raise RuntimeError(f"Failed to get projects: {response.reason}\nResponse contents:\n{response.text.decode()}")
            
        return projects_list

    def _get_project_tasks(self, project_id : str):
        # Doubt there'l be more than 5000 tasks for a project so just use 1st page!
        url = f"{self.BASE_URL}/workspaces/{self._config.workspace_id}/projects/{project_id}/tasks?page=1&page-size=5000"
        response = requests.get(url, headers={
            "X-Api-Key": self._config.api_key,
            "Content-Type": "application/json"
        })

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f"Failed to get tasks for project '{project_id}': {response.reason}\nResponse contents:\n{response.text.decode()}")

        tasks = response.json()

        return [ClockifyTask(id=task['id'], name=task['name']) for task in tasks]



clockify_cfg = read_config("config.json")
clockify = Clockify(clockify_cfg)
myprojects = clockify.get_projects()
pprint.pprint(myprojects)
sys.exit(1)


_start_time = None

def start_timer():
    global _start_time
    _start_time = datetime.now(timezone.utc).isoformat()
    payload = {
        "start": _start_time,
        "projectId": "67ecf1beedf9a1136e65242c",
        "description": DESCRIPTION,
        "taskId": "67ecf1beedf9a1136e65243a"
    }

    if PROJECT_ID:
        payload["projectId"] = PROJECT_ID

    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries"
    print(payload)
    print(_start_time)
    res = requests.post(url, headers=HEADERS, json=payload)

    if res.status_code == 201:
        print("Timer started.")
    else:
        print(f"Start failed: {res.status_code}")
        print(res.text)

    print(_start_time)

def stop_timer():
    global _start_time
    print(_start_time)
    # Get current user
    user_res = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    if user_res.status_code != 200:
        print("Failed to get user info.")
        return

    user_id = user_res.json()["id"]

    # Get currently running time entry
    running_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{user_id}/time-entries?in-progress=true"
    running_res = requests.get(running_url, headers=HEADERS)

    if running_res.status_code != 200:
        print("Failed to get running timer.")
        return

    entries = running_res.json()
    if not entries:
        print("No timer is running.")
        return

    print(entries)
    entry_id = entries[0]["id"]
    stop_time = datetime.now(timezone.utc).isoformat()
    stop_url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}"
    stop_payload = {"start": _start_time, "end": stop_time}
    stop_payload["projectId"] = "67ecf1beedf9a1136e65242c"
    stop_payload["taskId"] = "67ecf1beedf9a1136e65243a"
    print(stop_payload)
    stop_res = requests.put(stop_url, headers=HEADERS, json=stop_payload)

    if stop_res.status_code == 200:
        print("Timer stopped.")
    else:
        print(f"Stop failed: {stop_res.status_code}")
        print(stop_res.text)


def is_keyboard(device):
    return device.vendor_id != 0 and device.product_name and "SayoDevice 2x3P" in device.product_name.lower()

def on_data_handler(data):
    if data[8] == 16:
        print(f"PRESSED :{int((data[3] - 31) / 2 + 1)}")
        start_timer()

    elif data[8] == 17:
        print(f"RELEASED :  {data[3]}")
        stop_timer()





def main():
    projects()
    print("_"*80)
    list_active_tasks()
    print("_"*80)
    all_devices = hid.HidDeviceFilter().get_devices()
    sayo = None
    for dev in all_devices:
        if dev.product_name == "SayoDevice 2x3P":
            sayo = dev

    print(sayo)

    # Choose the second keyboard
    second_kb = sayo
    second_kb.open()
    second_kb.set_raw_data_handler(on_data_handler)

    print("Listening to second keyboard... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        second_kb.close()

if __name__ == "__main__":
    main()
