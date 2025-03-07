#!/bin/bash

######################################################
# MSDS434 - Section 55 - Winter '25
# dispatch-predictions: CI/CD pipeline
# 
# Kevin Geidel
# 
# ci.sh - Execute the CI/CD pipeline
######################################################

# Pull in new code
git pull

# Update package dependencies
pip install -r ../requirements.txt

# Run any new database migrations
python manage.py migrate