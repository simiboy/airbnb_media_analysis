import csv
import pandas as pd
import time
from openai import OpenAI
import time

# Record start time
start_time = time.time()

# DEFINING START AND END
start =  3512
end = 4000

# Initialize OpenAI client
client = OpenAI()

# Load questions from questions.csv
questions = []
with open('questions.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        questions.append(row['question'])

# Load articles from articles.csv
articles = pd.read_csv('articles.csv')

# Open articles_analyzed.csv for writing
with open('articles_analyzed.csv', mode='a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write header
    #header = list(articles.columns)
    #for question in questions:
    #    header.append(question)
    #writer.writerow(header)

    # Iterate through articles
    for i, article in articles.iterrows():
        if i+1 < start or i+1 >= end:
            continue  # Skip articles outside the specified range
        article_title = article['Title']
        article_text = article['Content']

        row_data = []

        # Iterate through questions for each article
        for j, question in enumerate(questions):
            print(f"Article {i+1}/{len(articles)}, question {j+1}/{len(questions)} - {article['Title'][:30]}")

            question = question.replace("[country]", article['Country'])

            # Shorten article_text if it exceeds maximum max length

            if len(article_text) > 15000:
                article_text = article_text[:15000]


            # Send article title, text, and question to OpenAI
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are analyzing newspaper articles in a framework where I always provide the article and ask questions that require yes or no (1/0) answer. This is article is titled {article_title}. The content of the article is the following: {article_text}"},
                    {"role": "user", "content": f"Answer this question with strictly one integer, 1 (for yes) or 0 (for no): {question}"}
                ]
            )

            # Get answer from OpenAI
            answer = completion.choices[0].message.content

            # Append answer to row data
            row_data.append(answer)

            # Wait a bit to avoid api overload
            time.sleep(2)

            # no need to do all the other questions if it is not about the country or airbnb
            if answer != '1' and j == 0:
                break
            
            continue

            # If answer is yes, ask for a short quotation
            if answer == '1':
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are analyzing newspaper articles. Provide short text answers in forms of quotations from the text. This is article is titled {article_title}. The content of the article is the following: {article_text}"},
                        {"role": "user", "content": f"Provide a short quotation from the article that supports a positive answer (yes) for this question: {question}"}
                    ]
                )

                # Get quotation from OpenAI
                quotation = completion.choices[0].message.content

                # Append quotation to row data
                row_data.append(quotation)
            else:
                row_data.append("")

        # Write row data to CSV
        writer.writerow(list(article.values) + row_data)

print("Analysis completed and stored in articles_analyzed.csv")
# Record end time
end_time = time.time()
# Print duration
print(f"Time taken: {end_time - start_time} seconds")