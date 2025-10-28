#!/bin/bash

# Bash script to create .env file

echo "🔧 H. pylori CDSS - Environment Setup"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Create .env file
cat > .env << 'EOF'
# H. pylori CDSS Configuration

# Model paths
SCREEN_MODEL_PATH=models/screening_hp_pos_calibrated.joblib
STAGE_MODEL_PATH=models/staging_3class.joblib

# Screening threshold (0.0 to 1.0)
SCREEN_THRESH=0.60

# JWT secret key (CHANGE THIS IN PRODUCTION!)
JWT_SECRET=change_me_to_a_secure_random_string_dev_only

# CORS allowed origins (comma-separated)
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:8000,http://localhost:5500

# Database URL (SQLite by default)
DATABASE_URL=sqlite:///./cdss.db
EOF

echo "✅ .env file created successfully!"
echo ""
echo "⚠️  IMPORTANT: Before running in production:"
echo "   1. Change JWT_SECRET to a secure random string"
echo "   2. Verify model paths are correct"
echo "   3. Update ALLOWED_ORIGINS for your domain"
echo ""
echo "Next steps:"
echo "   1. Ensure model files are in the models/ directory"
echo "   2. Run: ./run_api.sh"
echo "   3. Open: http://localhost:8000/ui/index.html"
echo ""
