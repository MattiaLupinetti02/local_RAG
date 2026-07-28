#!/bin/bash

set -e

echo "=========================================="
echo "      Avvio server Ollama"
echo "=========================================="

ollama serve &

SERVER_PID=$!

echo "Attendo che Ollama sia disponibile..."

until curl -s http://localhost:11434/api/tags > /dev/null
do
    sleep 2
done

echo ""
echo "Ollama pronto."
echo ""

#########################################
# Download embedding model (prima, serve per l'indice)
#########################################

if ! ollama list | grep -q "bge-m3"
then
    echo "Download modello bge-m3..."
    ollama pull bge-m3
else
    echo "bge-m3 già presente."
fi

#########################################
# Download modello LLM
#########################################

if ! ollama list | grep -q "llama3.2"
then
    echo "Download modello llama3.2..."
    ollama pull llama3.2
else
    echo "llama3.2 già presente."
fi

echo ""
echo "=========================================="
echo " Tutti i modelli sono disponibili"
echo "=========================================="

wait $SERVER_PID