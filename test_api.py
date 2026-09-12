import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["app"] == "Vadakkunokki.ai"

@pytest.mark.asyncio
async def test_startup_greeting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/chat/startup")
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert "message" in data

@pytest.mark.asyncio
async def test_chat_empty_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/chat", json={"session_id": "s1", "message": "   "})
    assert res.status_code == 400

@pytest.mark.asyncio
async def test_game_flow_and_unlock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Start Tic-Tac-Toe
        res_start = await ac.post("/api/game/start", json={"session_id": "sess_game_test", "game": "tic_tac_toe"})
        assert res_start.status_code == 200
        start_data = res_start.json()
        chal_id = start_data["challenge_id"]

        # 2. Attempt unlock before winning -> should be 403 Forbidden
        res_unlock_early = await ac.post("/api/challenge/answer", json={"session_id": "sess_game_test", "challenge_id": chal_id})
        assert res_unlock_early.status_code == 403

        # 3. Make moves
        res_move = await ac.post("/api/game/ttt-move", json={"session_id": "sess_game_test", "challenge_id": chal_id, "row": 0, "col": 0})
        assert res_move.status_code == 200
        move_data = res_move.json()
        assert move_data["board"][0][0] == "X"
