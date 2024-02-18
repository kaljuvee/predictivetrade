import pandas as pd
import openai
import json

# Initialize the OpenAI API with a hypothetical key
openai.api_key = "my_key"


def prepare_data(df):
    df['completion_prompt'] = df['action']
    to_train_df = df[['description', 'completion_prompt']].rename(columns={'description': 'prompt', 'completion_prompt': 'completion'})
    return to_train_df


    # Convert the chat data to JSONL format
    jsonl_file_path = "data/temp_data.jsonl"
    with open(jsonl_file_path, "w") as outfile:
        for entry in data:
            json.dump(entry, outfile)
            outfile.write('\n')
    return

def convert_to_chat_format(data):
    chat_data = []
    for record in data:
        chat_record = {
            "messages": [
                {"role": "user", "content": record["prompt"]},
                {"role": "assistant", "content": record["completion"]}
            ]
        }
        chat_data.append(chat_record)
    return chat_data


def get_random_news_sample(df):
    """Retrieve a random sample from the dataframe."""
    return df.sample(1).iloc[0]['description']

def test_fine_tuned_model(model_name, test_text):
    """Test the fine-tuned model with a sample text."""
    
    completion = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:personal::7xjpOjLW",
        messages=[
            {"role": "user", "content": random_news_text}
        ]
    )
    print(completion.choices[0].message['content'])


def main():
    # Reading the CSV file
    df = pd.read_csv('data/news_prices_biotech.csv')
    prepared_data = prepare_data(df)

    # Convert to chat format
    chat_format_training = convert_to_chat_format(data=prepared_data.to_dict('records'))

    # Create a file for fine-tuning
    jsonl_file_path = 'data/temp_data.jsonl'
    with open(jsonl_file_path, "w") as outfile:
        for entry in chat_format_training:
            json.dump(entry, outfile)
            outfile.write('\n')
    
    # Capture the response from the file creation
    response = openai.File.create(
        file=open(jsonl_file_path, "rb"),
        purpose='fine-tune'
    )
    
    # Extract the file ID from the response and start fine-tuning
    file_id = response["id"]
    fine_tuning_response = openai.FineTuningJob.create(training_file=file_id, model="gpt-3.5-turbo")
    
    # Wait for the fine-tuning to complete (for simplicity, we're just doing a retrieval without waiting)
    # In a real-world scenario, you'd probably want to poll this endpoint periodically to check the status
    fine_tuning_job = openai.FineTuningJob.retrieve(fine_tuning_response['id'])
    
    print("Fine-tuning job details:", fine_tuning_job)
    test_text = get_random_news_sample(df)
    print("Test text:", test_text)

if __name__ == "__main__":
    main()
