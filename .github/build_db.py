#!/usr/bin/env python3

import subprocess
import urllib.request
import os
import sys
import json
import time

def download_zipped(url):
    temp_file = "/tmp/existing.json"
    subprocess.run(['curl', '-L', '-o', temp_file, url], stderr=subprocess.STDOUT)
    result = subprocess.run(['unzip', '-p', temp_file], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    return result.stdout.decode()


def get_distribution_db():
    string = download_zipped("https://raw.githubusercontent.com/MiSTer-devel/Distribution_MiSTer/main/db.json.zip")
    return json.loads(string)


def download_unzipped(url):
    temp_file = "/tmp/existing.json"
    subprocess.run(['curl', '-L', '-o', temp_file, url], stderr=subprocess.STDOUT)
    with open(temp_file, 'r') as file:
        return file.read()


def get_linux_db():
    string = download_unzipped("https://raw.githubusercontent.com/theypsilon/LinuxDB_MiSTer/db/linuxdb.json")
    return json.loads(string)


def save_json(db, json_name):
    with open(json_name, 'w') as f:
        json.dump(db, f, sort_keys=True, separators=(',', ':'), indent=4)
    print('Saved ' + json_name)


def main():
    print('Getting distribution_mister db')
    distribution_db = get_distribution_db()

    print('Getting previous theypsilon/LinuxDB db')
    try:
        previous_linux_db = get_linux_db()
    except Exception as e:
        print('Failed:')
        print(e)
        print()
        previous_linux_db = {"linux": {}}

    if json.dumps(distribution_db["linux"]) == json.dumps(previous_linux_db["linux"]):
        print('Nothing to change!')
        return


    print('Building Linux DB...')

    db = {
        "db_id": 'theypsilon/LinuxDB',
        "files": {},
        "folders": {},
        "linux": distribution_db["linux"],
        "timestamp":  int(time.time())
    }

    save_json(db, 'linuxdb.json')

    dryrun = False
    if len(sys.argv) >= 2 and sys.argv[1] == '-d':
        print('Dry run!')
        dryrun = True

    if not dryrun:
        print('Pushing Linux DB!')
        subprocess.run(['git', 'config', '--global', 'user.email', 'theypsilon@gmail.com'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'The CI/CD Bot'], check=True)
        subprocess.run(['git', 'checkout', '--orphan','db'], check=True)
        subprocess.run(['git', 'reset'], check=True)
        subprocess.run(['git', 'add', 'linuxdb.json'], check=True)
        subprocess.run(['git', 'commit', '-m','Creating Linux DB'], check=True)
        subprocess.run(['git', 'push', '--force','origin', 'db'], check=True)

    return 0


if __name__ == '__main__':
    exit(main())
