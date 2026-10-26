#!/bin/bash

# Step 1: I am going to run bash scripts for each exercise in separate folders, at the home directory
cd ../..
exercise_directory="exercise2"

 # Only create if the exercise directory does not exist
if [  ! -d "$exercise_directory" ]; then
  mkdir "$exercise_directory"
fi
cd $exercise_directory || exit
# Step 2: Install nbconvert library that can be used to convert Jupyter notebooks to Python files
sudo apt-get update -y && sudo apt install python3-dev python3-pip python3-venv -y
 # Only create a virtual environment if it does not exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install nbconvert

# Step 3: create a directory deequv1 and go to it
mkdir deequv1
cd deequv1 || exit

# Step 4: clone GitHub repositories in repos.txt
# Getting the repos list from your input - the default value is ../repos_subset.txt
input="${1:-"repos_subset.txt"}"
input_path="../../DE2026/lab1/$input"
printf "Repository list path: %s\n" "$input_path"

while read -r repo; do
  echo "${repo}.git"| git clone "$repo"
done < "$input_path"

# Step 5: Get the paths of all Jupyter notebooks
find . -name '*ipynb' > "notebooks.txt"


# Step 6: Convert Jupyter notebooks to  python files

while read -r file; do
  jupyter nbconvert --to script "$file"
done < "notebooks.txt"

# Step 7: Merge all Python files into a single file
# \; is used with the find command's -exec option to mark the end of the command being run on found files.
find . -name '*.py' -exec cat {} \; > all_deequ.py
wc -l all_deequ.py

# Step 8: Count the occurrence of each keyword in the merged Python file. keywords in keywords.txt

keywords_list="../../DE2026/lab1/keywords.txt"
while read -r keyword; do
  grep -oh "$keyword" all_deequ.py | wc -w | awk -v var="$keyword" '{printf "%s:%s\n",var,$1;}' >> ../results_deeque.txt
done < "$keywords_list"