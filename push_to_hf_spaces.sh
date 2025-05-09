#!/bin/bash

# Temporarily use .gitignore_hf_spaces
mv .gitignore .gitignore_origin 
mv .gitignore_hf_spaces .gitignore

# Push to hf_spaces
git push -f hf_spaces main 

# Restore original .gitignore
mv .gitignore .gitignore_hf_spaces
mv .gitignore_origin .gitignore