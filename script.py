import requests
from os import environ
from typing import List, Dict
import logging

SOURCE_GRAFANA_AHTH_KEY = environ.get('SOURCE_GRAFANA_AHTH_KEY')
TARGET_GRAFANA_AUTH_KEY = environ.get('TARGET_GRAFANA_AUTH_KEY')

SOURCE_GRAFANA_URL = environ.get('SOURCE_GRAFANA_URL')
TARGET_GRAFANA_URL = environ.get('TARGET_GRAFANA_URL')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_source_notification_channels() -> List :
  
  headers = {
    "Authorization": f"Bearer {SOURCE_GRAFANA_AHTH_KEY}",
    "Content-Type": "application/json"
  }
  s = requests.Session()
  s.headers.update(headers)
  res = get_notification_channels(f"{SOURCE_GRAFANA_URL}/api/alert-notifications", s)
  return res


def get_notification_channels(url: str, session: requests.Session) -> List:

  def delete_non_unique_feilds(nc: Dict) -> Dict:
    del nc['created']
    del nc['updated']
    del nc['id']
    return nc

  res = session.get(url)
  res.raise_for_status()
  res_list = map(delete_non_unique_feilds, res.json())
  res_dict = { v['uid']: v for v in res_list}

  return res_dict
  res_list = [{"uid": "foo", "a": 1}, {"uid": "bar", "a": 2}]


def put_notification_channels(notification_channels: Dict):
  headers = {
    "Authorization": f"Bearer {TARGET_GRAFANA_AUTH_KEY}",
    "Content-Type": "application/json"
  }
  s = requests.Session()
  s.headers.update(headers)

  url = f"{TARGET_GRAFANA_URL}/api/alert-notifications"

  existing_notification_channels = get_notification_channels(url, s)
  
  logging.info("updating existing notification channels")
  new_nc_uids = set(notification_channels.keys()) - set(existing_notification_channels.keys())
  to_be_deleted_nc_uids = set(existing_notification_channels.keys()) - set(notification_channels.keys())

  #delete notification channels that no longer exsit in old
  for nc_uid in to_be_deleted_nc_uids:
    logging.info(f"deleting nc with UID: {nc_uid}")
    res = s.delete(f"{url}/uid/{nc_uid}")
    res.raise_for_status()


  #creating new notification channels
  for nc_uid in new_nc_uids:
    logging.info(f"creating new nc with UID: {nc_uid}")
    res = s.post(url, json=notification_channels[nc_uid])
    res.raise_for_status()

  # update exsiting (if needed) ingnore those that need to be deleted
  for nc_uid in set(existing_notification_channels.keys()) - to_be_deleted_nc_uids:
    if existing_notification_channels[nc_uid] != notification_channels[nc_uid]:
      logging.info(f"updating exsiting nc with UID: {nc_uid}")
      res = s.put(f"{url}/uid/{nc_uid}", json=notification_channels[nc_uid])
      res.raise_for_status()

def run():
  put_notification_channels(get_source_notification_channels())

if __name__ == "__main__":
  return 0
  if SOURCE_GRAFANA_AHTH_KEY == None:
    print("Source grafana auth key env var not set")
    exit(1)
  if TARGET_GRAFANA_AUTH_KEY == None:
    print("Target grafana auth key env var not set")
    exit(1)
  if SOURCE_GRAFANA_URL == None:
    print("Source grafana url env var not set")
    exit(1)
  if TARGET_GRAFANA_URL == None:
    print("Target grafana url env var not set")
    exit(1)
  
  run()
