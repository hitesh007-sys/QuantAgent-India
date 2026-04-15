import os
import pandas as pd

data_folder = "data"
files = os.listdir(data_folder)

print(f"Total files: {len(files)}\n")

for f in sorted(files):
    path = os.path.join(data_folder, f)
    df = pd.read_csv(path)
    print(f"{f}: {len(df)} rows, columns: {list(df.columns)}")