#!/bin/bash

# Step 1: I am going to run bash scripts for each exercise in separate folders, at the home directory
cd ../..
exercise_directory="exercise1"

 # Only create if the exercise directory does not exist
if [  ! -d "$exercise_directory" ]; then
  mkdir "$exercise_directory"
fi
cd $exercise_directory || exit

# Step 2: We are going to use the Python project in lab1/unit-test-example.
# Create a virtual environment and install dependencies required by it
sudo apt update -y &&  sudo apt install python3-dev python3-pip python3-venv -y
 # Only create a virtual environment if it does not exist
if [  ! -d ".venv"  ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate

python3 -m pip install -r ../DE2026/lab1/unit-test-example/requirements.txt

# Step 3: Run the unit tests (pytest) in the project
python3 -m pytest --junitxml=test_log.xml ../DE2026/lab1/unit-test-example/tests

# Step 4: Create a bucket in the Google Cloud Storge. Use the user provided name.
# When you are running the script, you can provide  it. e.g., sh live-lab-ex1.sh my_bucket_name
bucket_path="gs://$1"
printf "Bucket Path: %s\n" "$bucket_path"

bucket_name_retrieved=$(gcloud storage buckets describe "$bucket_path" --format="value(name)")
printf "Bucket Name Retrieved: %s\n" "$bucket_name_retrieved"

if [  "$bucket_name_retrieved" = "$1"  ]; then
     echo "A bucket is already available"
else
     gcloud storage buckets create "$bucket_path" \
      --default-storage-class=STANDARD \
      --location=US-CENTRAL1 \
      --uniform-bucket-level-access \
      --public-access-prevention
fi

# Step 5: Upload the test results to the bucket
gcloud storage cp test_log.xml "$bucket_path"