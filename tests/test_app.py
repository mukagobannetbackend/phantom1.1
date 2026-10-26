import io
import os
import pytest
from app import create_app, db
from app.models import User, Trade, Screenshot

@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / 'test.db'
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    os.environ['SECRET_KEY'] = 'test-secret'
    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False, UPLOAD_FOLDER=str(tmp_path / 'uploads'))
    with application.app_context():
        db.drop_all(); db.create_all()
    yield application
    with application.app_context():
        db.session.remove(); db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def register(client, email='trader@example.com', name='Test Trader'):
    return client.post('/auth/register', data={'display_name': name, 'email': email, 'password': 'password123'}, follow_redirects=True)

def login(client, email='trader@example.com'):
    return client.post('/auth/login', data={'email': email, 'password': 'password123'}, follow_redirects=True)

def test_health_is_public(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'service': 'phantomvault-pro', 'status': 'ok'}

def test_register_login_and_dashboard(client):
    response = register(client)
    assert response.status_code == 200
    assert b'Workspace overview' in response.data
    client.get('/auth/logout')
    response = login(client)
    assert response.status_code == 200
    assert b'Workspace overview' in response.data

def test_trade_lifecycle_and_analytics(client):
    register(client)
    response = client.post('/trades/new', data={'symbol': 'EURUSD', 'direction': 'Long', 'setup': 'MSS + FVG', 'outcome': 'Win', 'realized_r': '2.0', 'rule_adherence': 'on'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'EURUSD' in response.data
    analytics = client.get('/analytics')
    assert analytics.status_code == 200
    assert b'100.0%' in analytics.data
    assert b'2.00R' in analytics.data

def test_user_cannot_access_another_users_trade(client, app):
    register(client)
    with app.app_context():
        user = User.query.filter_by(email='trader@example.com').first()
        trade = Trade(user_id=user.id, symbol='GBPUSD', direction='Short')
        db.session.add(trade); db.session.commit(); trade_id = trade.id
    client.get('/auth/logout')
    register(client, 'other@example.com', 'Other User')
    assert client.get(f'/trades/{trade_id}').status_code == 404

def test_screenshot_upload_is_persisted_locally(client, app, tmp_path):
    register(client)
    client.post('/trades/new', data={'symbol': 'NAS100', 'direction': 'Short'}, follow_redirects=True)
    with app.app_context():
        trade = Trade.query.filter_by(symbol='NAS100').first()
        trade_id = trade.id
    image = io.BytesIO(b'fake image bytes')
    response = client.post(f'/trades/{trade_id}/screenshots', data={'file': (image, 'chart.png'), 'timeframe': '5M', 'caption': 'Entry'}, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        shot = Screenshot.query.first()
        assert shot is not None
        assert shot.timeframe == '5M'
        assert (tmp_path / 'uploads' / shot.filename).exists()

def test_coach_creates_versioned_review(client, app):
    register(client)
    client.post('/trades/new', data={'symbol': 'USDJPY', 'direction': 'Long', 'outcome': 'Loss', 'realized_r': '-1.0'}, follow_redirects=True)
    with app.app_context():
        trade = Trade.query.filter_by(symbol='USDJPY').first(); trade_id = trade.id
    response = client.post(f'/trades/{trade_id}/coach', follow_redirects=True)
    assert response.status_code == 200
    assert b'Process review' in response.data
    with app.app_context():
        trade = db.session.get(Trade, trade_id)
        assert len(trade.reviews) == 1
        assert trade.reviews[0].version == 1


def test_ai_coach_chat_uses_mock_response(client, app, monkeypatch):
    from types import SimpleNamespace
    import app.coach_routes as coach_routes

    register(client)

    class FakeOpenAI:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.fake_create)
            )

        def fake_create(self, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content="Mock coach reply: wait for liquidity confirmation."
                        )
                    )
                ]
            )

    monkeypatch.setattr(coach_routes, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")

    response = client.post(
        "/coach/api/chat",
        json={"message": "What confirmation should I wait for?"}
    )

    assert response.status_code == 200
    assert response.get_json()["reply"] == (
        "Mock coach reply: wait for liquidity confirmation."
    )
