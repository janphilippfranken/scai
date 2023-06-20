import pandas as pd
import numpy as np

def save_as_csv(episode, data_directory, episode_id, model):
    message_records = []
    for message_type, messages in episode.buffer.full_memory.message_dict.items():
        for msg in messages:
            message_records.append({
                'message_type': message_type, 
                'prompt': msg['prompt'],
                'response': msg['message'].content, 
                'rating': msg['rating'],
            })

    # Convert to dataframe
    df = pd.DataFrame(message_records)

    # Extract conversation id from 'message_type'
    df['conversation_id'] = df['message_type'].str.extract('(\d+)', expand=False)

    # Replace 'conversation_\d+_user' and 'conversation_\d+_assistant' with 'user' and 'assistant'
    df['message_type'] = df['message_type'].str.replace('conversation_\d+_user', 'user', regex=True)
    df['message_type'] = df['message_type'].str.replace('conversation_\d+_assistant', 'assistant', regex=True)
    df['message_type'] = df['message_type'].apply(lambda x: 'system' if 'system_message' in x else x)

    # Convert 'NaN' in 'conversation_id' to '-1' and then to integer, and then increment by 1
    df['conversation_id'] = df['conversation_id'].fillna(-1).astype(int) + 1
    # Replace system message conversation id with -1
    df.loc[df['message_type'] == 'system', 'conversation_id'] = -1

    # Save dataframe as csv
    df.to_csv(f'{data_directory}/{episode_id}_{model}.csv', index=False)