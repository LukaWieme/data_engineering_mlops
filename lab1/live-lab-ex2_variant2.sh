#!/bin/bash

# Step 1: I am going to run bash scripts for each exercise in separate folders, at the home directory
cd ../..
exercise_directory="exercise2"

 # Only create if the exercise directory does not exist
if [  ! -d "$exercise_directory" ]; then
  mkdir "$exercise_directory"
fi
cd $exercise_directory || exit

# Step 2: create a directory deequv2 and go to it
mkdir deequv2
cd deequv2 || exit

# Step 3: clone GitHub repositories in repos.txt
# Getting the repos list from your input - the default value is ../repos_subset.txt
input="${1:-"repos_subset.txt"}"
input_path="../../DE2026/lab1/$input"
printf "Repository list path: %s\n" "$input_path"

while read -r repo; do
  echo "${repo}.git"| git clone "$repo"
done < "$input_path"

# Step 4: Merge all Python files into a single file
# \; is used with the find command's -exec option to mark the end of the command being run on found files.
find . -name '*.py' -exec cat {} \; > all_deequ.py
wc -l all_deequ.py

# Step 5: Count the occurrence of each keyword in the merged Python file. keywords in keywords.txt

keywords_list="../../DE2026/lab1/keywords.txt"
while read -r keyword; do
  grep -oh "$keyword" all_deequ.py | wc -w | awk -v var="$keyword" '{printf "%s:%s\n",var,$1;}' >> ../results_deeque_without_notebooks.txt
done < "$keywords_list"