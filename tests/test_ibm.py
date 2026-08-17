import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.qs_bb84.ibm_backend import backend_listele

print("IBM Quantum baglantisi test ediliyor...\n")
backend_listele()