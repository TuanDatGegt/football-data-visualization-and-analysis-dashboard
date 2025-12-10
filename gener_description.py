import pandas as pd
import ast
import json

def gener_action_Description(events_path, tags_path, output_path):
    events_df = pd.read_csv(events_path)
    tags_df = pd.read_csv(tags_path)


    tags_dict = dict(zip(tags_df['Tag'], tags_df['Description']))

    events_df['tags'] = events_df['tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

    def map_tags_to_description(tag_list):
        return [tags_dict.get(tag['id'], str(tag['id'])) for tag in tag_list]
    
    events_df['tag_descriptions'] = events_df['tags'].apply(map_tags_to_description)

    events_df['description'] = events_df.apply(
        lambda row: ', '.join(row['tag_descriptions']) if row['tag_descriptions'] else 'No specific tags',
        axis=1
    )

    summary_df = events_df[['subEventName', 'description']].copy()

    summary_df['count'] = summary_df.groupby(['subEventName', 'description'])['subEventName'].transform('count')

    summary_df = summary_df.drop_duplicates(subset=['subEventName', 'description'])

    summary_df = summary_df.sort_values(by='count', ascending=False)

    summary_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print('Đã lưu file vào thư mục: {output_path}')

    return summary_df


