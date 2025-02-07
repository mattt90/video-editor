import episode_processor
import thumbnail_editor
import sys
import os

upload_file = 'test3.json'
if (len(sys.argv) > 1):
    upload_file = sys.argv[1]

options = episode_processor.get_options(upload_file)

thumbnail_editor.build_thumbnail(options)
#episode_processor.process_episode(options)