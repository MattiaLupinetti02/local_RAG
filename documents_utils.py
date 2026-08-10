
import os
import json

def make_file_set(filelist:json):
    file_set = set()
    for f in filelist:
        file_set.add(f["file"])
    return file_set

def build_context(documents: list):
    if not documents:
        return ""
    return "\n\n---\n\n".join(f"{doc['text']}\n {doc['score']}" for doc in documents)