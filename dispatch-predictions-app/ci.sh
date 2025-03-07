#!/bin/bash

######################################################
# MSDS434 - Section 55 - Winter '25
# dispatch-predictions: CI/CD pipeline
# 
# Kevin Geidel
# 
# ci.sh - Execute the CI/CD pipeline
######################################################

# NOTE: This will run from django project root!
# (not main project root! Since its called by DRF!)

echo CI/CD IS RUNNING!

# Pull in new code
cd .. && git pull

# Update package dependencies
pip install -r requirements.txt

# Run any new database migrations
cd dispatch-predictions && python manage.py migrate