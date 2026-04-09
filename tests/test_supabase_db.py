from unittest.mock import MagicMock, patch

from chat_pt.supabase_db import SupabaseDB


@patch("chat_pt.supabase_db.get_secret")
@patch("chat_pt.supabase_db.create_client")
def test_supabase_init(mock_create_client, mock_get_secret):
    """Test Supabase initialization."""
    mock_get_secret.side_effect = lambda key, default=None: "fake_val"
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    db = SupabaseDB()
    assert db.client == mock_client
    mock_create_client.assert_called_once_with("fake_val", "fake_val")


@patch("chat_pt.supabase_db.get_secret")
@patch("chat_pt.supabase_db.create_client")
def test_supabase_create_user(mock_create_client, mock_get_secret):
    """Test user creation in Supabase."""
    mock_get_secret.return_value = "fake"
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock the chain: client.table().insert().execute()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute
    mock_execute.data = [{"id": "uuid-123"}]

    db = SupabaseDB()
    user_id = db.create_user("Test", "test@example.com")

    assert user_id == "uuid-123"
    mock_client.table.assert_called_with("users")
    mock_table.insert.assert_called_once()


@patch("chat_pt.supabase_db.get_secret")
@patch("chat_pt.supabase_db.create_client")
def test_supabase_nutrition_plans(mock_create_client, mock_get_secret):
    """Test nutrition plan operations in Supabase."""
    mock_get_secret.return_value = "fake"
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    db = SupabaseDB()

    # Mock get_nutrition_plan
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"plan_json": {"calories": 2000}}
    ]
    plan = db.get_nutrition_plan("consult-123")
    assert plan == {"calories": 2000}
    mock_client.table.assert_called_with("nutrition_plans")

    # Mock save_nutrition_plan (insert case)
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    db.save_nutrition_plan("user-123", "consult-123", {"calories": 2100})
    # Verify it tried to insert
    mock_client.table.return_value.insert.assert_called()


@patch("chat_pt.supabase_db.get_secret")
@patch("chat_pt.supabase_db.create_client")
def test_supabase_coaching_profile(mock_create_client, mock_get_secret):
    """Test coaching profile operations in Supabase."""
    mock_get_secret.return_value = "fake"
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    db = SupabaseDB()

    # Mock get_coaching_profile
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"profile_json": {"goal": "lose weight"}}
    ]
    profile = db.get_coaching_profile("user-123")
    assert profile == {"goal": "lose weight"}
    mock_client.table.assert_called_with("user_coaching_profile")
