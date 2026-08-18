# 01 - Data Analysis

This notebook is the first stage of the project.
Do not modify the raw CSV.

## 1. Imports
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

## 2. Load data
```python
df = pd.read_csv("../data/raw/APY.csv")
print("Shape:", df.shape)
df.head()
```

## 3. Profile
```python
df.info()
df.describe(include="all")
```

## 4. Missing values
```python
df.isnull().sum()
```

## 5. Unique values
```python
for col in ["State", "District", "Crop", "Season", "Crop_Year"]:
    print("\n", col)
    print(df[col].nunique())
```

## 6. Duplicate rows
```python
print("Duplicates:", df.duplicated().sum())
```

## 7. Numeric validity
```python
print("Negative Area:", (df["Area"] < 0).sum())
print("Negative Production:", (df["Production"] < 0).sum())
print("Negative Yield:", (df["Yield"] < 0).sum())
```

## 8. Zero production
```python
print("Zero Production:", (df["Production"] == 0).sum())
```

## 9. Yield distribution
```python
df["Yield"].describe()
```

Continue the analysis only after inspecting these results.
