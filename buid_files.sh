# Update pip
python3.9 -m pip install --upgrade pip

# Install virtualenv
pip install virtualenv

# Create a new virtual environment
virtualenv venv

# Activating virtual environment
# On Windows: venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run collectstatic (assuming you have it defined in your Django project)
python3.9 manage.py collectstatic
