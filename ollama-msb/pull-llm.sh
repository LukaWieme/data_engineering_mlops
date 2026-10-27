#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &

# Pause for Ollama to start.
sleep 10

echo "Retrieve tinyllama model..."
ollama pull tinyllama
echo "Done!"