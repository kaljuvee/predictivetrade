
# Activate virtual environment if applicable
echo "Activate virtual environment..."
#source venv/Scripts/activate
source venv/bin/activate

# Install or update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Pull latest changes from Git
echo "Pulling latest changes from Git..."
git pull

# Stop existing Streamlit app
echo "Stopping Streamlit app..."
pkill streamlit

# Start Streamlit app
echo "Starting Streamlit app..."
streamlit run Home.py&
