import pandas as pd

df = pd.read_csv("heart.csv")
print("Columns in your CSV:")
print(df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
