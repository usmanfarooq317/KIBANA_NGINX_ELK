# Containerized Flask Apps with Load Balancing and Logging

## 📋 Project Overview

This project demonstrates a containerized Flask application setup with:
- **3 Flask applications** (app1, app2, app3) running in separate containers
- **Nginx load balancer** that routes requests sequentially (3 requests per container)
- **Fluent Bit** for centralized logging and log processing
- **Automatic container rotation** based on request count

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose
- curl (for testing)

### 1. Clone and Navigate to Project
```bash
# Clone your project
# Navigate to project directory
cd project-directory
```

### 2. Build and Start Services
```bash
# Stop any existing containers and remove volumes
docker-compose down -v

# Build and start all services
docker-compose up --build -d
```

### 3. Verify Services are Running
```bash
docker ps
```
You should see 5 containers:
- nginx (load balancer)
- app1, app2, app3 (Flask applications)
- fluent-bit (log processor)

## 🌐 Access Applications

### Load Balancer (Port 8001)
```bash
# Access through browser or curl
http://localhost:8001

# Or using curl
curl http://localhost:8001
```

### Direct Access to Individual Apps
```bash
# Add these ports to docker-compose.yml if needed:
# app1: "5001:5001"
# app2: "5002:5001" 
# app3: "5003:5001"

# Then access:
# http://localhost:5001 (app1)
# http://localhost:5002 (app2)
# http://localhost:5003 (app3)
```

## 📊 Request Routing Logic

### How Requests are Distributed:
1. **First 3 requests** → Container 1 (app1)
2. **Next 3 requests** → Container 2 (app2)  
3. **Next 3 requests** → Container 3 (app3)
4. **Cycle repeats** back to Container 1

### Request Flow:
```
Client Request → Nginx → 
    ↓
Check current container availability →
    ↓
If container has handled < 3 requests → Serve request
    ↓
If container has handled 3 requests → Return 503 error
    ↓
Nginx detects 503 → Try next container
```

### ⏱️ Recommended Time Between Requests

| Scenario | Recommended Delay | Reason |
|----------|------------------|---------|
| **Testing rotation** | 0.5 - 1 second | Allows clear observation of container switching |
| **Production testing** | 2 - 5 seconds | Simulates realistic user behavior |
| **Load testing** | No delay | For maximum throughput testing |
| **Debugging** | 3 - 5 seconds | Gives time to check logs between requests |

**Example test script with delay:**
```bash
# Test with 1-second delay between requests
for i in {1..10}; do
  echo "Request #$i"
  curl -s http://localhost:8001/ | grep "Container #" | head -2
  sleep 1  # 1-second delay
done
```

## 📝 Logging System

### Where Logs Are Stored

#### 1. **Inside Containers (Primary Storage)**
```
/fluent-bit/logs/app1/app1.log    # App1 logs (Container 1)
/fluent-bit/logs/app2/app2.log    # App2 logs (Container 2)  
/fluent-bit/logs/app3/app3.log    # App3 logs (Container 3)
```

#### 2. **Docker Volumes (Persistent Storage)**
```bash
# View volume information
docker volume ls | grep nginx-elk

# Expected volumes:
# nginx-elk_app1-logs
# nginx-elk_app2-logs  
# nginx-elk_app3-logs
```

#### 3. **Fluent Bit Output**
- **Console output**: Processed JSON logs in fluent-bit container
- **No persistent file output**: Configured for console only

### How to View Logs

#### **Method 1: View Processed Logs via Fluent Bit**
```bash
# View real-time processed logs (JSON format)
docker logs -f fluent-bit

# View last 50 lines
docker logs --tail 50 fluent-bit

# Follow logs with timestamps
docker logs -f --timestamps fluent-bit
```

#### **Method 2: View Raw Logs from Each Container**
```bash
# One command to view all app logs
for app in app1 app2 app3; do
  echo "========== $app LOGS =========="
  docker exec nginx-elk-${app}-1 cat /fluent-bit/logs/$app/$app.log 2>/dev/null || echo "No logs found"
  echo ""
done
```

#### **Method 3: Check Individual Container Logs**
```bash
# App1 logs
docker exec nginx-elk-app1-1 cat /fluent-bit/logs/app1/app1.log

# App2 logs  
docker exec nginx-elk-app2-1 cat /fluent-bit/logs/app2/app2.log

# App3 logs
docker exec nginx-elk-app3-1 cat /fluent-bit/logs/app3/app3.log
```

#### **Method 4: Tail Logs in Real-Time**
```bash
# Tail all logs simultaneously (separate terminals)
# Terminal 1:
docker exec -it nginx-elk-app1-1 tail -f /fluent-bit/logs/app1/app1.log

# Terminal 2:
docker exec -it nginx-elk-app2-1 tail -f /fluent-bit/logs/app2/app2.log

# Terminal 3:
docker exec -it nginx-elk-app3-1 tail -f /fluent-bit/logs/app3/app3.log
```

### Log Format Examples

#### **Raw Log Format (app1.log)**
```json
{
  "timestamp": "2025-12-12T07:30:45.123456",
  "appname": "APP1",
  "log_level": "INFO",
  "message": "HOME endpoint accessed",
  "color": "#007bff",
  "container_number": 1,
  "container_id": "nginx-elk-app1-1",
  "request_counter": 1,
  "max_requests": 3,
  "client_ip": "172.18.0.1",
  "path": "/",
  "request_number": 1,
  "status": "handling"
}
```

#### **Fluent Bit Processed Output**
```json
{
  "date": 1733995845,
  "timestamp": "2025-12-12T07:30:45.123456",
  "appname": "APP1",
  "log_level": "INFO",
  "message": "HOME endpoint accessed",
  "color": "#007bff",
  "container_number": 1,
  "container_id": "nginx-elk-app1-1",
  "request_counter": 1,
  "max_requests": 3
}
```

## 🛠️ Management Commands

### Health Checks
```bash
# Check health through load balancer
curl http://localhost:8001/health

# Check individual app health (if ports exposed)
curl http://localhost:5001/health  # app1
curl http://localhost:5002/health  # app2  
curl http://localhost:5003/health  # app3
```

### Container Status
```bash
# View request counters and availability
curl http://localhost:8001/status

# Expected response format:
# {
#   "app": "app1",
#   "container": 1,
#   "requests_handled": 2,
#   "max_requests": 3,
#   "remaining_requests": 1,
#   "status": "available"
# }
```

### Reset Request Counters
```bash
# Reset all containers' request counters
curl http://localhost:8001/reset

# Response:
# {"message": "Request counter reset", "container": 1, "request_counter": 0}
```

### Service Management
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes logs)
docker-compose down -v

# Restart specific service
docker-compose restart app1

# View service logs
docker-compose logs -f nginx
docker-compose logs -f app1
```

## 🔧 Configuration

### Project Structure
```
project/
├── app1/              # Flask app1 (Container 1)
│   ├── app.py        # Application code
│   ├── Dockerfile    # Container definition
│   └── requirements.txt
├── app2/              # Flask app2 (Container 2)
├── app3/              # Flask app3 (Container 3)
├── nginx/
│   ├── nginx.conf    # Load balancing configuration
│   └── Dockerfile
├── fluent-bit/
│   └── fluent-bit.conf  # Log processing configuration
└── docker-compose.yml   # Service orchestration
```

### Key Configuration Files

#### **docker-compose.yml** - Main Settings
```yaml
# Change these values as needed:
ports:
  - "8001:80"          # Change host port if 8001 is busy

environment:
  MAX_REQUESTS: 3      # Change number of requests per container
```

#### **Flask Apps** - Container Settings
```python
# In app.py files:
MAX_REQUESTS = 3       # Requests per container before switching
COLOR = "#007bff"      # Background color for web interface
CONTAINER_NUMBER = 1   # Container identifier (1, 2, or 3)
```

#### **Nginx** - Load Balancing
```nginx
# In nginx.conf:
server app1:5001 max_fails=1 fail_timeout=5s;  # Health check settings
proxy_next_upstream error timeout http_503 http_504;  # When to retry
```

## 🧪 Testing Scenarios

### Scenario 1: Basic Rotation Test
```bash
# Make 10 requests with 0.5s delay
for i in {1..10}; do
  echo "=== Request $i ==="
  curl -s http://localhost:8001/ | grep -E "Container #|Request #"
  sleep 0.5
done
```

### Scenario 2: Monitor Logs While Testing
```bash
# Terminal 1: Watch Fluent Bit logs
docker logs -f fluent-bit

# Terminal 2: Send test requests
for i in {1..12}; do
  curl -s http://localhost:8001/ > /dev/null
  echo "Sent request $i"
  sleep 1
done
```

### Scenario 3: Reset and Retest
```bash
# Reset counters
curl http://localhost:8001/reset

# Verify reset
curl http://localhost:8001/status

# Test fresh rotation
for i in {1..6}; do
  curl -s http://localhost:8001/
  sleep 1
done
```

## 🐛 Troubleshooting

### Common Issues

#### **1. Port 8001 Already in Use**
```bash
# Check what's using port 8001
sudo lsof -i :8001

# Stop the conflicting service or
# Change port in docker-compose.yml:
# ports:
#   - "8002:80"  # Use different host port
```

#### **2. Fluent Bit Not Starting**
```bash
# Check Fluent Bit logs
docker logs fluent-bit

# Common issue: Configuration errors
# Solution: Check fluent-bit.conf syntax
```

#### **3. Containers Not Rotating**
```bash
# Check if containers return 503 after 3 requests
for i in {1..4}; do
  curl -v http://localhost:8001/ 2>&1 | grep "HTTP/"
  sleep 1
done

# Reset counters if stuck
curl http://localhost:8001/reset
```

#### **4. No Logs Appearing**
```bash
# Check if logs directories exist
docker exec nginx-elk-app1-1 ls -la /fluent-bit/logs/

# Check if apps are writing logs
docker exec nginx-elk-app1-1 tail -f /fluent-bit/logs/app1/app1.log

# Generate test logs
curl http://localhost:8001/test-log
```

### Debug Commands
```bash
# Check all container status
docker-compose ps

# View detailed container information
docker inspect nginx-elk-app1-1

# Check container resource usage
docker stats

# View nginx access logs
docker-compose logs -f nginx

# Shell into container for debugging
docker exec -it nginx-elk-app1-1 /bin/bash
```

## 📈 Monitoring

### View Current State
```bash
# Check all containers' status
echo "=== Container Status ==="
for app in app1 app2 app3; do
  echo -n "$app: "
  docker exec nginx-elk-${app}-1 curl -s http://localhost:5001/status | jq -r '.status'
done

# Check request distribution
echo -e "\n=== Request Counters ==="
for app in app1 app2 app3; do
  echo -n "$app: "
  docker exec nginx-elk-${app}-1 curl -s http://localhost:5001/status | jq -r '.requests_handled'
done
```

### Performance Testing
```bash
# Rapid fire test (no delay)
for i in {1..100}; do
  curl -s http://localhost:8001/ > /dev/null &
done

# Check logs after test
docker logs --tail 100 fluent-bit | grep "container_number" | sort | uniq -c
```

## 🧹 Cleanup

### Complete Cleanup
```bash
# Stop and remove all containers, networks, volumes
docker-compose down -v

# Remove all Docker volumes (warning: deletes all data)
docker volume prune -f

# Remove unused Docker images
docker image prune -f
```

### Partial Cleanup
```bash
# Stop services but keep volumes (preserve logs)
docker-compose down

# Remove specific volume
docker volume rm nginx-elk_app1-logs

# Remove specific container
docker rm nginx-elk-app1-1
```

## 📚 Additional Information

### Architecture Diagram
```
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Nginx     │
                    │  (Load      │
                    │  Balancer)  │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼─────┐     ┌────▼─────┐     ┌────▼─────┐
    │  App1    │     │  App2    │     │  App3    │
    │(Container│     │(Container│     │(Container│
    │    1)    │     │    2)    │     │    3)    │
    └────┬─────┘     └────┬─────┘     └────┬─────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                    ┌─────▼─────┐
                    │ Fluent Bit│
                    │ (Logging) │
                    └───────────┘
```

### Time Estimates
| Action | Estimated Time |
|--------|----------------|
| Initial build | 2-3 minutes |
| Container restart | 10-20 seconds |
| Request cycle (3 requests) | 3-15 seconds (with delays) |
| Log processing | Near real-time |

### Best Practices
1. **Use delays** between requests when testing rotation (1-2 seconds)
2. **Check logs frequently** during testing
3. **Reset counters** between test scenarios
4. **Monitor Fluent Bit** for JSON parsing errors
5. **Use different browsers/tabs** to simulate multiple users

---

