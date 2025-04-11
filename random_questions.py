import pandas as pd
import random
import os

# Path to the input CSV file
input_file = os.path.join('data', 'quiz_data.csv')

# Path to the output CSV file
output_file = os.path.join('data', 'random_quiz_data.csv')

# Read the CSV file
df = pd.read_csv(input_file)

# Get unique difficulty levels
difficulty_levels = df['level'].unique()

# Initialize an empty list to store the selected questions
selected_questions = []

# For each difficulty level, randomly select 10 questions
for level in difficulty_levels:
    # Get all questions of this difficulty
    level_questions = df[df['level'] == level]
    
    # If there are less than 10 questions, take all of them
    if len(level_questions) <= 10:
        selected = level_questions
    else:
        # Randomly select 10 questions
        selected = level_questions.sample(n=10, random_state=42)
    
    # Add the selected questions to our list
    selected_questions.append(selected)

# Combine all selected questions into a single DataFrame
result_df = pd.concat(selected_questions)

# Save the selected questions to a new CSV file
result_df.to_csv(output_file, index=False)

print(f"Successfully selected questions and saved to {output_file}")
print(f"Questions selected per difficulty level:")
for level in difficulty_levels:
    count = len(result_df[result_df['level'] == level])
    print(f"- {level}: {count} questions") 