
# Activate virtual environment if applicable
echo "Activate virtual environment..."
source venv/bin/activate

# Install or update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Pull latest changes from Git
echo "Pulling latest changes from Git..."
git pull

# Start Streamlit app
echo "Starting Streamlit app..."
nohup streamlit run Home.py &
