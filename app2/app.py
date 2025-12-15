from flask import Flask, jsonify, request
import os, datetime, pathlib, json

app = Flask(__name__)

APP_NAME = "app2"
COLOR = "#28a745"   # green
CONTAINER_NUMBER = 2
CONTAINER_ID = os.getenv('HOSTNAME', 'container-2')

# Request counter for this container
request_counter = 0
MAX_REQUESTS = 3  # This container handles 3 requests before switching

LOG_DIR = f"/fluent-bit/logs/{APP_NAME}"
LOG_FILE = f"{LOG_DIR}/{APP_NAME}.log"

# Create directory
pathlib.Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

def write_log(msg, level="INFO", request_data=None):
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Create structured log entry optimized for Kibana
    log_entry = {
        "@timestamp": timestamp,
        "timestamp": timestamp,
        "appname": APP_NAME.upper(),
        "application": APP_NAME.upper(),
        "log_level": level,
        "level": level,
        "message": msg,
        "color": COLOR,
        "container_number": CONTAINER_NUMBER,
        "container_id": CONTAINER_ID,
        "request_counter": request_counter,
        "max_requests": MAX_REQUESTS,
        "client_ip": request.remote_addr if request else None,
        "path": request.path if request else None,
        "http_method": request.method if request else None,
        "service": "flask-app",
        "environment": "development",
        "host": CONTAINER_ID,
        "tags": ["flask", "python", "microservice"]
    }
    
    # Add request data if provided
    if request_data:
        log_entry.update(request_data)
    
    # Add container-specific tags
    log_entry["tags"].append(f"container-{CONTAINER_NUMBER}")
    log_entry["tags"].append(f"app-{APP_NAME}")
    
    # Print to stdout (for Docker logs)
    print(json.dumps(log_entry))
    
    # Write to file
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Failed to write log: {e}")

@app.route("/")
def home():
    global request_counter
    request_counter += 1
    
    write_log("HOME endpoint accessed", request_data={
        "request_number": request_counter,
        "status": "handling" if request_counter <= MAX_REQUESTS else "redirecting"
    })
    
    if request_counter <= MAX_REQUESTS:
        next_container = 3 if CONTAINER_NUMBER == 2 else 1 if CONTAINER_NUMBER == 3 else 2
        return f"""
        <html>
        <head>
            <title>{APP_NAME.upper()} - Container {CONTAINER_NUMBER}</title>
            <style>
                body {{
                    background: {COLOR};
                    color: white;
                    font-family: Arial, sans-serif;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                    margin: 0;
                }}
                .app-name {{
                    font-size: 60px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .container-info {{
                    font-size: 30px;
                    margin-bottom: 10px;
                }}
                .request-info {{
                    font-size: 24px;
                    margin-top: 20px;
                    background: rgba(255,255,255,0.2);
                    padding: 10px 20px;
                    border-radius: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="app-name">{APP_NAME.upper()}</div>
            <div class="container-info">Container #{CONTAINER_NUMBER}</div>
            <div class="container-info">ID: {CONTAINER_ID}</div>
            <div class="request-info">Request #{request_counter} of {MAX_REQUESTS} on this container</div>
            <div class="request-info">Next request will go to Container #{next_container}</div>
        </body>
        </html>
        """
    else:
        # Reset counter and indicate should redirect
        request_counter = 0
        return jsonify({
            "app": APP_NAME,
            "container": CONTAINER_NUMBER,
            "container_id": CONTAINER_ID,
            "status": "max_requests_reached",
            "message": f"Container {CONTAINER_NUMBER} handled {MAX_REQUESTS} requests, redirecting to next container"
        }), 503

@app.route("/health")
def health():
    write_log("Health check endpoint accessed")
    return jsonify({
        "status": "healthy",
        "app": APP_NAME,
        "container": CONTAINER_NUMBER,
        "container_id": CONTAINER_ID,
        "color": COLOR,
        "request_counter": request_counter,
        "max_requests": MAX_REQUESTS,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200

@app.route("/reset")
def reset():
    global request_counter
    request_counter = 0
    write_log("Request counter reset")
    return jsonify({
        "message": "Request counter reset",
        "container": CONTAINER_NUMBER,
        "request_counter": request_counter
    })

@app.route("/status")
def status():
    return jsonify({
        "app": APP_NAME,
        "container": CONTAINER_NUMBER,
        "container_id": CONTAINER_ID,
        "requests_handled": request_counter,
        "max_requests": MAX_REQUESTS,
        "remaining_requests": max(0, MAX_REQUESTS - request_counter),
        "status": "available" if request_counter < MAX_REQUESTS else "full"
    })

if __name__ == "__main__":
    write_log(f"Starting {APP_NAME} (Container {CONTAINER_NUMBER}) on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=False)