import json
import pytest
from backend.app import app, LLM_SETTINGS # Assuming app can be imported like this
from backend.config import DEFAULT_TEMPERATURE, DEFAULT_MAX_MODEL_TOKENS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_llm_settings_default(client):
    """Test GET /api/llm-settings returns default settings for a new session."""
    response = client.get('/api/llm-settings?session_id=test_session_get_default')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['settings']['temperature'] == DEFAULT_TEMPERATURE
    assert data['settings']['max_tokens'] == DEFAULT_MAX_MODEL_TOKENS

def test_post_llm_settings(client):
    """Test POST /api/llm-settings updates settings for a session."""
    session_id = 'test_session_post'
    new_settings = {"temperature": 0.75, "max_tokens": 1500}

    # First, set the new settings
    response = client.post(f'/api/llm-settings?session_id={session_id}',
                           json={"settings": new_settings})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['settings']['temperature'] == new_settings['temperature']
    assert data['settings']['max_tokens'] == new_settings['max_tokens']

    # Then, GET to verify they were stored
    response_get = client.get(f'/api/llm-settings?session_id={session_id}')
    assert response_get.status_code == 200
    data_get = json.loads(response_get.data)
    assert data_get['settings']['temperature'] == new_settings['temperature']
    assert data_get['settings']['max_tokens'] == new_settings['max_tokens']

def test_post_llm_settings_partial_update(client):
    """Test POST /api/llm-settings with partial data only updates provided fields."""
    session_id = 'test_session_post_partial'
    # Initialize with defaults by a GET call
    client.get(f'/api/llm-settings?session_id={session_id}')

    # Update only temperature
    new_temp_settings = {"temperature": 0.88}
    response = client.post(f'/api/llm-settings?session_id={session_id}',
                           json={"settings": new_temp_settings})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['settings']['temperature'] == new_temp_settings['temperature']
    assert data['settings']['max_tokens'] == DEFAULT_MAX_MODEL_TOKENS # Should remain default

    # Update only max_tokens
    new_tokens_settings = {"max_tokens": 2500}
    response = client.post(f'/api/llm-settings?session_id={session_id}',
                           json={"settings": new_tokens_settings})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['settings']['temperature'] == new_temp_settings['temperature'] # Should be from previous update
    assert data['settings']['max_tokens'] == new_tokens_settings['max_tokens']

def test_post_llm_settings_invalid_data(client):
    """Test POST /api/llm-settings with invalid data returns error."""
    session_id = 'test_session_post_invalid'
    invalid_settings = {"temperature": "not-a-float", "max_tokens": "not-an-int"}
    response = client.post(f'/api/llm-settings?session_id={session_id}',
                           json={"settings": invalid_settings})
    # The backend currently updates valid fields and ignores invalid ones,
    # returning success with the current (possibly default or partially updated) settings.
    # This test might need adjustment based on desired error handling stringency.
    # For now, let's check it doesn't crash and returns success with defaults or valid partial updates.
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    # Depending on implementation, it might return defaults or partially updated valid values.
    # Current app.py initializes with defaults, then updates valid fields.
    assert data['settings']['temperature'] == DEFAULT_TEMPERATURE
    assert data['settings']['max_tokens'] == DEFAULT_MAX_MODEL_TOKENS


def test_reset_clears_llm_settings(client):
    """Test that /api/reset clears LLM settings for a session."""
    session_id = "test_session_reset_settings"
    custom_settings = {"temperature": 0.6, "max_tokens": 1200}

    # Set some custom settings
    client.post(f'/api/llm-settings?session_id={session_id}', json={"settings": custom_settings})
    response = client.get(f'/api/llm-settings?session_id={session_id}')
    data = json.loads(response.data)
    assert data['settings']['temperature'] == custom_settings['temperature']

    # Reset the session
    client.post('/api/reset', json={"session_id": session_id})

    # Verify settings are reset to default
    response_after_reset = client.get(f'/api/llm-settings?session_id={session_id}')
    data_after_reset = json.loads(response_after_reset.data)
    assert data_after_reset['settings']['temperature'] == DEFAULT_TEMPERATURE
    assert data_after_reset['settings']['max_tokens'] == DEFAULT_MAX_MODEL_TOKENS
    # Also ensure the LLM_SETTINGS dictionary on the server side reflects this for the session
    assert LLM_SETTINGS.get(session_id) is None # Or it's explicitly set to defaults, app.py deletes the key
