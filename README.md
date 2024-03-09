# Deploying Streamlit App on EC2 Instance

## Step 1: Connect to the EC2 Instance

- Use SSH with your key pair to connect to your instance:
  ```
  ssh -i "predictivetrade.pem" ubuntu@ec2-13-48-105-67.eu-north-1.compute.amazonaws.com
  ```

## Step 2: Install Required Software on EC2 Instance

### Update the System:
- Run the following commands to update your system:
  ```
  sudo apt update
  sudo apt upgrade
  ```

### Install Required Software:
- Install Python, pip, development tools, and Nginx:
  ```
  sudo apt install python3-pip python3-dev python3-venv nginx
  ```

## Step 3: Set Up Virtual Environment and Deploy Streamlit App

### Clone Your Streamlit App:
- Clone your Streamlit application from GitHub:
  ```
  git clone https://github.com/kaljuvee/predictivetrade.git
  ```

### Create and Activate the Virtual Environment:
- Set up a Python virtual environment and activate it (Linux):
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

- Set up a Python virtual environment and activate it (Windows/VS Code / Bash):
  ```
  python -m venv venv
  source venv/Scripts/activate
  ```
  
- Install dependencies from the `requirements.txt` file:
  ```
  pip install -r requirements.txt
  ```

## Step 4: Configure Nginx as a Reverse Proxy

### Create a Nginx Server Block:
- Edit the Nginx configuration for your app:
  ```
  sudo nano /etc/nginx/sites-available/predictivetrade
  ```

### Configure the Server Block:
- Add the following configuration to proxy requests to the Streamlit app:

  ```nginx
  server {
      listen 80;
      server_name predictivetrade;

      location / {
          proxy_pass http://localhost:8501;  # Streamlit default port
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection 'upgrade';
          proxy_set_header Host $host;
          proxy_cache_bypass $http_upgrade;
      }
  }
  ```

### Enable the Nginx Server Block:
- Enable the configuration and restart Nginx:
  ```
  sudo ln -s /etc/nginx/sites-available/predictivetrade /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl restart nginx
  ```

## Step 5: Configure SSL with Let's Encrypt

### Install Certbot:
- Add the Certbot repository and install Certbot:
  ```
  sudo rm /etc/apt/sources.list.d/certbot-ubuntu-certbot-jammy.list
  sudo apt update
  sudo snap install --classic certbot
  sudo ln -s /snap/bin/certbot /usr/bin/certbot


  ```

### Obtain SSL Certificate:
- Obtain an SSL certificate for the two domains:
  ```
  sudo certbot --nginx
  ```

## Step 6: Launch the Streamlit Application

- Run your Streamlit app:
  ```
  streamlit run Home.py
  ```
  This should launch a browser on `localhost:8501`.

## Killing / Restarting Streamlikt

  ```
  pkill -f 'streamlit run Home.py'
  streamlit run Home.py &
  ```

