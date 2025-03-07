#!/bin/bash

######################################################
# MSDS434 - Section 55 - Winter '25
# dispatch-predictions: CI/CD pipeline
# 
# Kevin Geidel
# 
# ci.sh - Execute the CI/CD pipeline
######################################################

echo CI/CD IS RUNNING!

# Pull in new code
git pull

# Update package dependencies
pip install -r ../requirements.txt

# Run any new database migrations
cd dispatch-predictions-app && python manage.py migrate