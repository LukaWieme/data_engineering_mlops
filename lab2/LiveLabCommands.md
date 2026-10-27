# Active 1: Dockerize Training-API Component 

## Create volume directories 

mkdir models 

## Build the image and run the container 

sudo docker build -t indikakuma/training-api:0.0.1 .

sudo docker run -p  5002:5000 -v /home/indika_kuma/models:/usr/src/trainapp/models -d --name=training-api indikakuma/training-api:0.0.1

## Create firewall rule

gcloud compute firewall-rules create flask-port-3 --allow tcp:5002

# Active 2: Ollama and Open WebUI 

## We are going to use two named volumes for Ollama and the Web UI).  We can use docker volume create 

sudo docker volume create ollama

sudo docker volume create open-webui

## Pull the official Ollama image

sudo docker pull ollama/ollama:0.34.1

## Run Ollama container

sudo docker run -d --name ollama -v ollama:/root/.ollama -p 11434:11434  ollama/ollama:0.34.1

## Build Open-webUI custom image

sudo docker build -t open-webui-custom:0.0.1 .

## Create a container from it

sudo docker run -d -p 8080:8080 --add-host=host.docker.internal:host-gateway  -e OLLAMA_BASE_URL=http://ollama:11434 -v open-webui:/app/backend/data --name open-webui open-webui-custom:0.0.1


## Create a Docker Network between the Ollama and Open WebUI containers  

sudo docker network create ollama-network 

sudo docker network connect ollama-network ollama

sudo docker network connect ollama-network open-webui

## Create the firewall rule for open web ui

gcloud compute firewall-rules create open-webui-port --allow tcp:8080

# Active 3: Docker Multi-stage Build

## Stop and delete running ollama container

sudo docker stop ollama

sudo docker rm ollama

sudo docker ps -a

## Clean the Ollama data from the previous container

sudo docker volume rm ollama

sudo docker volume create ollama


## Go back to the DE2026/lab2/ollama-msb and build the custom Ollama Docker image

cd DE2026/lab2/ollama-msb

sudo docker build -t custom-ollama:0.0.1 .

## Create the Ollama container from the new image and add it to the container network

sudo docker run -d --name ollama -v ollama:/root/.ollama -p 11434:11434  custom-ollama:0.0.1

sudo docker network connect ollama-network ollama

# Use the Ollama API (get inferences from an LLM) directly (in the VM)

curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "Why is Docker?",
  "stream": false
}’

# To access API from your laptop, create a firewall rule

gcloud compute firewall-rules create ollama-api-port --allow tcp:11434

# see https://docs.ollama.com/api/introduction

