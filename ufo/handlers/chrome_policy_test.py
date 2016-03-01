"""Test chrome policy module functionality."""

import json
import unittest

import flask
import mock

import ufo
from ufo import base_test


class ChromePolicyTest(base_test.BaseTest):
  """Test chrome policy functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(ChromePolicyTest, self).setUp()
    super(ChromePolicyTest, self).setup_config()

  @mock.patch('flask.render_template')
  def testChromePolicyRenderTemplate(self, mock_render_template):
    """Test the chrome policy handler renders the page.

    Args:
      mock_render_template: A mocked instance of flask.render_template on
                            which to assert about call arguments.
    """
    mock_render_template.return_value = ''
    self.client.get(flask.url_for('display_chrome_policy'))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('chrome_policy.html', args[0])
    json_data = json.loads(kwargs['policy_json'])
    self.assertIn('proxy_server_keys', json_data)
    self.assertIn('enforce_proxy_server_validity', json_data)
    self.assertNotIn('enforce_network_jail', json_data)
    self.assertIn('enforce_proxy_server_validity', kwargs)
    self.assertIn('enforce_network_jail', kwargs)

  def testChromePolicyDownload(self):
    """Test the chrome policy download handler downloads json."""
    resp = self.client.get(flask.url_for('download_chrome_policy'))

    json_data = json.loads(resp.data)
    self.assertIn('proxy_server_keys', json_data)
    self.assertIn('enforce_proxy_server_validity', json_data)
    self.assertNotIn('enforce_network_jail', json_data)

  def testEditValuesForPolicyConfig(self):
    """Test posting with modified policy config values updates in the db."""
    config = ufo.get_user_config()
    initial_proxy_server_config = config.proxy_server_validity
    initial_network_jail_config = config.network_jail_until_google_auth
    data_to_post = {
        'enforce_proxy_server_validity': json.dumps(not initial_proxy_server_config),
        'enforce_network_jail': json.dumps(not initial_network_jail_config),
    }

    resp = self.client.post(flask.url_for('edit_policy_config'),
                            data=data_to_post, follow_redirects=False)

    updated_config = ufo.get_user_config()
    self.assertEqual(not initial_proxy_server_config,
                     updated_config.proxy_server_validity)
    self.assertEqual(not initial_network_jail_config,
                     updated_config.network_jail_until_google_auth)
    self.assert_redirects(resp, flask.url_for('display_chrome_policy'))

if __name__ == '__main__':
  unittest.main()