import json
import thumbnail_editor
import video_processor
from moviepy.editor import AudioFileClip, concatenate_videoclips, vfx, VideoFileClip
import sys
import os

def behavior_intro(resource, intro_options):
    if intro_options is None:
        return resource
    intro_video = VideoFileClip(intro_options["video_path"]).without_audio().fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
    intro_audio = AudioFileClip(intro_options["audio_path"])
    return video_processor.process_intro(intro_video, intro_audio, resource, intro_options["fade"])

def behavior_outro(resource, outro_options):
    if outro_options is None:
        return resource
    outro_video = VideoFileClip(outro_options["video_path"]).without_audio().fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
    outro_audio = AudioFileClip(outro_options["audio_path"])
    return video_processor.process_outro(outro_video, outro_audio, resource, outro_options["fade"])

def behavior_speed_up(resource, speed_up_options):
    return video_processor.process_montage_video(resource, speed_up_options["rate"], speed_up_options["fade"], speed_up_options["background_audio_volume"])

def behavior_snip(resource, options):
    clips = []
    for clip in options["subclips"]:
        r = resource.subclip(clip["start"], clip["end"])
        clips.append(r)
    return concatenate_videoclips(clips)

def behavior_combine(resource, combine_options):
    clips = [resource]
    for clip in combine_options["clips"]:
        r = VideoFileClip(clip["path"])
        if ("subclip" in clip["subclip"] and clip["subclip"]["enabled"]):
            print(clip["subclip"])
            r = r.subclip(clip["subclip"]["start"], clip["subclip"]["end"])
        clips.append(r)
    return concatenate_videoclips(clips)

def process_folder_scene(resource):
    clips = []
    for file in os.listdir(resource["path"]):
        if (file.endswith(resource["extension"])):
            clips.append(VideoFileClip(resource["path"] + "/" + file))
    return concatenate_videoclips(clips)

def process_scene(scene):
    scene_resource = scene["resource"]
    resource = None
    if ("isFolder" in scene_resource and scene_resource["isFolder"]):
        return process_folder_scene(scene_resource)
    else:
        resource = VideoFileClip(scene_resource["path"])
        if ("subclip" in scene_resource and scene_resource["subclip"]["enabled"]):
            resource = resource.subclip(scene_resource["subclip"]["start"], scene_resource["subclip"]["end"])

    if "behaviors" in scene:
        print("Behavior exists")
        for behavior in scene["behaviors"]:
            if behavior["key"] == "intro":
                #resource = behavior_intro(resource, behavior["value"])
                pass
            elif behavior["key"] == "outro":
                pass
                #resource = behavior_outro(resource, behavior["value"])
            elif behavior["key"] == "speed_up":
                resource = behavior_speed_up(resource, behavior["value"])
            elif behavior["key"] == "combine":
                resource = behavior_combine(resource, behavior["value"])
            elif behavior["key"] == "snip":
                resource = behavior_snip(resource, behavior["value"])
            elif behavior["key"] == "quite":
                resource = resource.without_audio()
            else:
                raise Exception(f'behavior: "{behavior["key"]}" does not exist!')

    return resource

def process_scenes(video_processor):
    clips = []
    for scene in video_processor["scenes"]:
        clips.append(process_scene(scene))
    return clips

def get_options(upload_file_path):
    episode_file = open(upload_file_path)

    episode_data = json.load(episode_file)

    episode_file.close()

    return episode_data

def process_episode(episode_data):
    #thumbnail_output_format = episode_data["thumbnailOutputFormat"]
    #thumbnail_output = thumbnail_output_format.format(**episode_data)
    #print(thumbnail_output)

    #thumbnail_editor.create_thumbnail(episode_data["episode_number"], episode_data["thumbnail_output"])
    #thumbnail_editor.create_thumbnail(episode_data["episode_number"], thumbnail_output)
    thumbnail_editor.build_thumbnail(episode_data)

    processor_settings = episode_data["video_processor"]
    clips = process_scenes(processor_settings)

    final_video = concatenate_videoclips(clips)
    final_video = behavior_intro(final_video, processor_settings.get("intro"))
    final_video = behavior_outro(final_video, processor_settings.get("outro"))
    print(final_video.duration / 60.0)
    output_format = episode_data["output_format"]
    output_path = output_format.format(**episode_data)
    final_video.write_videofile(output_path, threads = episode_data["threads"])

#upload_file = 'upload.json'
#if (len(sys.argv) > 1):
#    upload_file = sys.argv[1]

#options = get_options(upload_file)
#process_episode(options)
