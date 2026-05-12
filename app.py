from app import create_app
from app import env_bool
from app import socketio
import os

app = create_app()

if __name__ == "__main__":
    socketio.run(
        app,
        debug=env_bool("FLASK_DEBUG", True),
        use_reloader=env_bool("FLASK_USE_RELOADER", False),
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", 5001)),
    )
