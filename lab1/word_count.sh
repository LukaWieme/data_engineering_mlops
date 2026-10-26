#!/bin/bash

# Step 1: Go back to the home directory and create a folder to be used for unzipping words.zip
cd ../..
directory="words"

 # Only create if the words directory does not exist
if [ ! -d "$directory" ]; then
  mkdir "$directory"
fi

# Step 2: Download the words.zip file from the GitHub URL and unzip it
wget https://github.com/IndikaKuma/DE2026/raw/refs/heads/main/lab1/words.zip  # you can also copy words.zip file from lab1
sudo apt update -y && sudo apt install unzip
unzip words.zip -d "$directory"

# Step 3: Create the results folder in the home directory
# Only create if the results directory does not exist
if [ ! -d "results" ]; then
  mkdir "results"
fi

# Step 4: Loop through all files in a directory and count words in each; save the results

for file in "$directory"/*; do
    if [ -f "$file" ]; then
        filename=$(basename -- "$file")
        result_file_path="results/${filename%.*}_wc.txt"
        echo "$result_file_path"
        tr -s '[:space:]' '\n' < "$file" | sort | uniq -c | sort -nr  > "$result_file_path"
    fi
done

# Step 5: Clean up
rm -rf "words"
rm "words.zip"
