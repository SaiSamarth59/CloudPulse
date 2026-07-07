# ☁️ CloudPulse

> Production-grade REST API deployed on AWS with automated CI/CD, monitoring, and load testing.

[![Deploy](https://github.com/SaiSamarth59/CloudPulse/actions/workflows/deploy.yml/badge.svg)](https://github.com/SaiSamarth59/CloudPulse/actions)

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                             │
│                           │                                 │
│                    [User / Browser]                         │
│                           │                                 │
│              ┌────────────▼────────────┐                    │
│              │      API Gateway        │  HTTPS             │
│              │  (HTTP API, AWS managed)│                    │
│              └────────────┬────────────┘                    │
│                           │                                 │
│         ┌─────────────────▼──────────────────────┐         │
│         │              AWS VPC                    │         │
│         │   ┌─────────────────────────────────┐  │         │
│         │   │     Security Group               │  │         │
│         │   │  (port 80 open, 22 = my IP only) │  │         │
│         │   │                                 │  │         │
│         │   │  ┌──────────────────────────┐  │  │         │
│         │   │  │    EC2 t2.micro           │  │  │         │
│         │   │  │    Ubuntu 22.04           │  │  │         │
│         │   │  │    Nginx → Gunicorn       │  │  │         │
│         │   │  │    Flask App (port 5000)  │  │  │         │
│         │   │  └──────────┬───────────────┘  │  │         │
│         │   └─────────────┼───────────────────┘  │         │
│         │                 │                       │         │
│         │    ┌────────────▼──────┐  ┌──────────┐ │         │
│         │    │   S3 Bucket       │  │CloudWatch│ │         │
│         │    │  (logs/backups)   │  │(metrics+ │ │         │
│         │    └───────────────────┘  │ alarms)  │ │         │
│         │                           └──────────┘ │         │
│         └────────────────────────────────────────┘         │
│                                                             │
│   ┌─────────────────────────────────┐                       │
│   │        GitHub Actions           │                       │
│   │  push to main → SSH → deploy    │──────────────────────►│
│   └─────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10 |
| Framework | Flask 3.0 + Gunicorn |
| Web Server | Nginx (reverse proxy) |
| Cloud | AWS EC2, S3, API Gateway, CloudWatch, IAM |
| CI/CD | GitHub Actions |
| Load Testing | Locust |
| OS | Ubuntu 22.04 LTS |

---

## 📁 Project Structure

```
CloudPulse/
├── app/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── templates/          # HTML templates (if any)
├── infrastructure/
│   └── setup.sh            # EC2 bootstrap script
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions CI/CD
├── locustfile.py           # Load testing script
├── screenshots/            # All monitoring & pipeline screenshots
└── README.md               # This file
```

---

## 🚀 Deployment Guide (Step by Step)

### Prerequisites
- AWS account
- GitHub account
- Windows machine with Git, Python, VS Code installed

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/SaiSamarth59/CloudPulse.git
cd CloudPulse
```

---

### Step 2 — Launch EC2 on AWS

1. Go to **AWS Console → EC2 → Launch Instance**
2. Settings:
   - Name: `cloudpulse-server`
   - AMI: Ubuntu Server 22.04 LTS
   - Type: t2.micro
   - Key pair: create `cloudpulse-key.pem`, download it
   - Security Group: port 22 (My IP), port 80 (Anywhere)
3. Click **Launch Instance**
4. Copy the **Public IPv4 address**

---

### Step 3 — Connect to EC2

```bash
# Windows — in CloudPulse folder
icacls cloudpulse-key.pem /inheritance:r /grant:r "saisa:R"
ssh -i cloudpulse-key.pem ubuntu@51.21.181.164
```

---

### Step 4 — Deploy App on EC2

```bash
sudo apt update -y && sudo apt install python3-pip python3-venv nginx -y
git clone https://github.com/SaiSamarth59/CloudPulse.git
cd CloudPulse/app
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create systemd service:
```bash
sudo tee /etc/systemd/system/cloudpulse.service << EOF
[Unit]
Description=CloudPulse Flask App
After=network.target
[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/CloudPulse/app
Environment="PATH=/home/ubuntu/CloudPulse/app/venv/bin"
ExecStart=/home/ubuntu/CloudPulse/app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable cloudpulse && sudo systemctl start cloudpulse
```

Configure Nginx:
```bash
sudo tee /etc/nginx/sites-available/cloudpulse << EOF
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
sudo ln -s /etc/nginx/sites-available/cloudpulse /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

Test: open `http://51.21.181.164` in browser → should return CloudPulse JSON.

---

### Step 5 — Configure CI/CD (GitHub Actions)

1. Go to GitHub repo → **Settings → Secrets → Actions → New secret**
2. Add:
   - `EC2_HOST` = your EC2 public IP
   - `EC2_SSH_KEY` = full contents of `cloudpulse-key.pem`
3. Push any change to main → pipeline runs automatically

---

### Step 6 — Set Up CloudWatch Monitoring

```bash
# On EC2
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
# (paste config JSON and start agent — see infrastructure/setup.sh)
```

- Go to **CloudWatch → Alarms → Create alarm** → CPU > 70% → name `cloudpulse-cpu-high`
- Go to **CloudWatch → Dashboards → Create** → `CloudPulse-Dashboard`

---

### Step 7 — Run Load Test

```bash
# Windows terminal
pip install locust
cd CloudPulse
locust -f locustfile.py --host=http://51.21.181.164
```

Open `http://localhost:8089` → 50 users, spawn rate 5 → Start swarming → let run 3 minutes → screenshot results.

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Project info and timestamp |
| `/health` | GET | Health check (returns 200) |
| `/metrics` | GET | App version and uptime status |

---

## 🔒 Security

- SSH restricted to deployer IP only (port 22)
- IAM role with least privilege (CloudWatch + S3 only)
- No credentials hardcoded anywhere
- S3 bucket is fully private
- GitHub Secrets used for all sensitive values

---

## 📸 Screenshots

All screenshots are in the `screenshots/` folder:
- `(1) Deploy Flask App on EC2.png` — App response in browser
- `(2) CICD with GitHub Actions.png` — Successful pipeline run
- `(3) CloudWatch Monitoring.png` — Monitoring dashboard
- `(4) Load Testing with Locust.png` — Load test output

---

## 📈 Load Testing Results

- Tool: Locust
- Users: 50 concurrent
- Duration: 3 minutes
- Avg response time: ~80–150ms
- Peak RPS: ~45–60
- Error rate: < 1%

---

## 🔮 Future Improvements

- Add HTTPS via AWS Certificate Manager
- Dockerize the application
- Add Terraform for infrastructure as code
- Auto Scaling Group + Load Balancer for production
- Add pytest unit tests in CI pipeline

---

## 👤 Author

**SaiSamarth** — CloudPulse 2026
