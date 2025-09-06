import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("Task 3 and 4_Loan_Data (1).csv")

# Use only required columns and drop missing values
data = df[['fico_score', 'default']].dropna()
fico_scores = np.array(sorted(data['fico_score']))
n = len(fico_scores)
num_buckets = 5  # You can adjust this

# Step 1: Precompute Mean Squared Error for each range
mse_table = np.zeros((n, n))
for i in range(n):
    for j in range(i, n):
        segment = fico_scores[i:j+1]
        avg = np.mean(segment)
        mse_table[i][j] = np.mean((segment - avg) ** 2)

# Step 2: Initialize Dynamic Programming tables
dp = np.full((n, num_buckets + 1), np.inf)
path = np.full((n, num_buckets + 1), -1)

# Base case: one bucket
for i in range(n):
    dp[i][1] = mse_table[0][i]

# Fill DP table
for b in range(2, num_buckets + 1):
    for i in range(b - 1, n):
        for j in range(b - 2, i):
            total_mse = dp[j][b - 1] + mse_table[j + 1][i]
            if total_mse < dp[i][b]:
                dp[i][b] = total_mse
                path[i][b] = j

# Step 3: Reconstruct bucket boundaries
boundaries = []
i = n - 1
b = num_buckets
while b > 0:
    split = int(path[i][b])
    boundaries.append((split + 1, i))
    i = split
    b -= 1

boundaries.reverse()

# Generate bucket boundaries
bucket_boundaries = []
for start, end in boundaries:
    bucket_boundaries.append((int(fico_scores[start]), int(fico_scores[end])))

print("\nFICO Buckets (based on score similarity):")
for i, (low, high) in enumerate(bucket_boundaries, 1):
    print(f"Bucket {i}: {low} to {high}")
print("✅ Bucketing completed successfully.")

# Step 4: Create rating map (lower rating = better score)
rating_map = {}
for rating, (low, high) in enumerate(bucket_boundaries, start=1):
    for score in range(low, high + 1):
        rating_map[score] = rating

print("\nSample Rating Map (first 10 entries):")
for score in sorted(rating_map.keys())[:10]:
    print(f"FICO Score: {score}, Rating: {rating_map[score]}")

# Step 5: Assign rating to each borrower
df['Rating'] = df['fico_score'].apply(lambda x: rating_map.get(int(x), np.nan))

# Step 6: Calculate PD per rating bucket
pd_per_bucket = df.groupby('Rating')['default'].mean()
print("\nProbability of Default by Rating Bucket:")
print(pd_per_bucket)

# Optional: Step 7: Plot histogram
plt.hist(data['fico_score'], bins=[b[0] for b in bucket_boundaries] + [bucket_boundaries[-1][1] + 1], edgecolor='black')
plt.title("FICO Score Distribution and Buckets")
plt.xlabel("FICO Score")
plt.ylabel("Number of Borrowers")
plt.grid(True)
plt.show()
