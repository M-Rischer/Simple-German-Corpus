import spacy
import torch
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

print(f"Spacy version: {spacy.__version__}")
print(f"PyTorch version: {torch.__version__}")
print(f"NumPy version: {np.__version__}")
print(f"Pandas version: {pd.__version__}")

model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v1")
print("SentenceTransformer model loaded successfully!")
