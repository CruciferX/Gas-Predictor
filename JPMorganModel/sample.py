import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load the data
df = pd.read_csv("loan_data.csv")  # File should be in the same folder

# Not using customer_id in prediction
df = df.drop(columns=["customer_id"])

# Separate features and target
X = df.drop(columns=["default"])
y = df["default"]

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a logistic regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict probabilities for test data
pred_probs = model.predict_proba(X_test)[:, 1]  # prob that default = 1
pred_labels = model.predict(X_test)

# Evaluate performance
print("Accuracy:", accuracy_score(y_test, pred_labels))
print("Confusion Matrix:\n", confusion_matrix(y_test, pred_labels))
print("Classification Report:\n", classification_report(y_test, pred_labels))

# Calculate Expected Loss for each prediction
recovery_rate = 0.10  # given
expected_loss = []

for i in range(len(X_test)):
    prob = pred_probs[i]
    loan_amt = X_test.iloc[i]["loan_amt_outstanding"]
    loss = prob * loan_amt * (1 - recovery_rate)
    expected_loss.append(loss)

# Add PD and EL to the output dataframe
output = X_test.copy()
output["PD"] = pred_probs
output["Expected_Loss"] = expected_loss
output["Actual_Default"] = y_test.values

# Save to CSV for analysis
output.to_csv("expected_loss_results.csv", index=False)
print("Results saved to expected_loss_results.csv")
