import episode_processor
import os

def upload_episode(episode_number):
    upload_file = f'upload_{episode_number}.json'
    path = f'D:/recording/outputs/e{episode_number}' #do better
    if not os.path.exists(path):
        os.mkdir(path)

    options = episode_processor.get_options(upload_file)
    episode_processor.process_episode(options)

upload_episode(142)
upload_episode(143)
upload_episode(144)