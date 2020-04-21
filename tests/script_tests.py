import pytest
import responses
import requests
import json

import script


SINGLE_NC_RESPONSE = [
  {
    'id': 1,
    'uid': "some-uid",
    'name': "nc_name",
    'type': "email",
    'isDefault': False,
    'sendReminder': False,
    'disableResolveMessage': False,
    'frequency': "",
    'created': "2017-11-22T08:53:20Z",
    'updated': "2017-11-22T08:53:20Z",
    'settings': {
      'addresses': "someEmai@foo.bar",
      'autoResolve': True,
      'httpMethod': "POST",
      'uploadImage': True
    }
  }
]



SOURCE_GRAFANA_RESPONSE = [
    {
    'id': 1,
    'uid': "some-uid-in-source",
    'name': "nc_name",
    'type': "email",
    'isDefault': False,
    'sendReminder': False,
    'disableResolveMessage': False,
    'frequency': "",
    'created': "2017-11-22T08:53:20Z",
    'updated': "2017-11-22T08:53:20Z",
    'settings': {
      'addresses': "someEmai@foo.bar",
      'autoResolve': True,
      'httpMethod': "POST",
      'uploadImage': True
    }
  },
  {
    'id': 2,
    'uid': "some-uid-not-needed-to-be-updated",
    'name': "not-needed-to-be-updated",
    'type': "email",
    'isDefault': False,
    'sendReminder': False,
    'disableResolveMessage': False,
    'frequency': "",
    'created': "2017-11-22T08:53:20Z",
    'updated': "2017-11-22T08:53:20Z",
    'settings': {
      'addresses': "someEmai@foo.bar",
      'autoResolve': True,
      'httpMethod': "POST",
      'uploadImage': True
    }
  },
  {
    'id': 3,
    'uid': "some-uid-that-needs-to-be-updated",
    'name': "not-needed-to-be-updated",
    'type': "email",
    'isDefault': False,
    'sendReminder': False,
    'disableResolveMessage': False,
    'frequency': "",
    'created': "2017-11-22T08:53:20Z",
    'updated': "2017-11-22T08:53:20Z",
    'settings': {
      'addresses': "newEmail@foo.bar",
      'autoResolve': True,
      'httpMethod': "POST",
      'uploadImage': True
    }
  }
]


TARGET_GRAFANA_RESPONSE = [
  {
    'id': 4,
    'uid': "some-uid-that-needs-to-be-deleted",
    'name': "nc_name",
    'type': "email",
    'isDefault': False,
    'sendReminder': False,
    'disableResolveMessage': False,
    'frequency': "",
    'created': "2017-11-22T08:53:20Z",
    'updated': "2017-11-22T08:53:20Z",
    'settings': {
      'addresses': "someEmai@foo.bar",
      'autoResolve': True,
      'httpMethod': "POST",
      'uploadImage': True
    }
  },
  {
    'id': 5,
    'uid': "some-uid-not-needed-to-be-updated",
    'name': "not-needed-to-be-updated",
    'type': "email",
    'isDefault': False,
    'sendReminder': False,
    'disableResolveMessage': False,
    'frequency': "",
    'created': "2017-11-22T08:53:20Z",
    'updated': "2017-11-22T08:53:20Z",
    'settings': {
      'addresses': "someEmai@foo.bar",
      'autoResolve': True,
      'httpMethod': "POST",
      'uploadImage': True
    }
  },
  {
    'id': 3,
    'uid': "some-uid-that-needs-to-be-updated",
    'name': "not-needed-to-be-updated",
    'type': "email",
    'isDefault': False,
    'sendReminder': False,
    'disableResolveMessage': False,
    'frequency': "",
    'created': "2017-11-22T08:53:20Z",
    'updated': "2017-11-22T08:53:20Z",
    'settings': {
      'addresses': "oldEmail@foo.bar",
      'autoResolve': True,
      'httpMethod': "POST",
      'uploadImage': True
    }
  }
]



@responses.activate
def test_get_notification_channels():
  url = 'http://some_grafan_url/api/alert-notifications'
  responses.add(responses.GET, url, status=200, json=SINGLE_NC_RESPONSE)
  result = script.get_notification_channels(url, requests)
  assert len(result) == 1
  #make sure we didn't delete all
  assert len(result['some-uid'].keys()) > 1
  # make sure we removed all keys we don't want
  assert not 'created' in result['some-uid'].keys()
  assert not 'id' in result['some-uid'].keys()
  assert not 'updated' in result['some-uid'].keys()


@responses.activate
def test_create_update_delete():
  source_grafana_url = 'http://source_grafana/'
  target_grafana_url = 'http://target_grafana/'
  script.SOURCE_GRAFANA_URL = source_grafana_url
  script.TARGET_GRAFANA_URL = target_grafana_url

  responses.add(responses.GET, url=f'{source_grafana_url}/api/alert-notifications', status=200, json=SOURCE_GRAFANA_RESPONSE)
  responses.add(responses.GET, url=f'{target_grafana_url}/api/alert-notifications', status=200, json=TARGET_GRAFANA_RESPONSE)
  responses.add(responses.DELETE, url=f'{target_grafana_url}/api/alert-notifications/uid/some-uid-that-needs-to-be-deleted', status=200)
  responses.add(responses.PUT, f'{target_grafana_url}/api/alert-notifications/uid/some-uid-that-needs-to-be-updated', status=201)
  responses.add(responses.POST, url=f'{target_grafana_url}/api/alert-notifications', status=200)
  script.run()

  def get_request_by_url_and_method(url:str, method:str):
    for call in responses.calls:
      if call.request.method == method and call.request.url == url:
        return call
    return None

  update_call = get_request_by_url_and_method(f'{target_grafana_url}/api/alert-notifications/uid/some-uid-that-needs-to-be-updated', 'PUT') 
  assert update_call != None

  delete_call = get_request_by_url_and_method(f'{target_grafana_url}/api/alert-notifications/uid/some-uid-that-needs-to-be-deleted', 'DELETE')
  assert delete_call != None
  
  # note this this test case contains a single create call
  create_call = get_request_by_url_and_method(f'{target_grafana_url}/api/alert-notifications', 'POST')
  assert create_call != None
  create_call_body = json.loads(create_call.request.body)
  assert create_call_body['uid'] == 'some-uid-in-source'