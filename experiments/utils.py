import pandas as pd

def save_as_csv(episode, data_directory, episode_id, model):
    message_records = []
    for message_type, messages in episode.buffer.full_memory.message_dict.items():
        for msg in messages:
            message_records.append({
                'message_type': message_type, 
                'content': msg['message'].content, 
                'rating': msg['rating']
            })
    # convert to dataframe and save as csv
    pd.DataFrame(message_records).to_csv(f'{data_directory}/{episode_id}_{model}.csv', index=False)