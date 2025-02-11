import os
import sys
import uvicorn
from app.main import app

def get_port():
    """Get port from environment variable or default to 5000"""
    try:
        # Try to get port from environment
        port_str = os.environ.get("PORT")
        if port_str:
            # Remove any quotes or whitespace
            port_str = port_str.strip().strip("'").strip('"')
            return int(port_str)
        return 5000
    except Exception as e:
        print(f"Error getting port: {e}")
        return 5000

if __name__ == "__main__":
    port = get_port()
    print(f"Starting server on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
