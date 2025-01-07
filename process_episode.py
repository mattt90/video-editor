import episode_processor
import sys
import os

upload_file = 'upload.json'
if (len(sys.argv) > 1):
    upload_file = sys.argv[1]

options = episode_processor.get_options(upload_file)

path = 'D:/recording/outputs/e' + options["episode_number"] #do better
if not os.path.exists(path):
    os.mkdir(path)

episode_processor.process_episode(options)