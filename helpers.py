import uuid
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Vadakkunokki] %(message)s"
)
logger = logging.getLogger("vadakkunokki")

def generate_id(prefix: str = "vada") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

def current_timestamp() -> float:
    return time.time()

def log_event(event_type: str, session_id: str, **kwargs):
    # Ensure sensitive credentials are never logged per FR-058
    clean_kwargs = {k: v for k, v in kwargs.items() if "key" not in k.lower() and "token" not in k.lower()}
    logger.info(f"EVENT: {event_type} | Session: {session_id} | Details: {clean_kwargs}")
