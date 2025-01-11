import json
import thumbnail_editor
import video_processor
import numpy
from moviepy.editor import AudioFileClip, concatenate_videoclips, vfx, VideoFileClip
from moviepy.video.VideoClip import ImageClip
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

def combine(values):
    clips = []
    for resource in values["resources"]:
        if (resource["key"] == "createimagevideo"):
            clips.append(create_image_video(resource["value"]))

    v = concatenate_videoclips(clips)

    if ("audio" in values and len(values["audio"]) > 0):
        print(values["audio"])
        v = v.set_audio(AudioFileClip(values["audio"]).subclip(0, v.duration))
        if ("volume" in values):
            v = v.volumex(values["volume"])

    return v

def create_image_video(values):
    image = None
    l = None
    a = None
    for step in values["image_steps"]:
        image = thumbnail_editor.process_image_step(step["key"], step["values"], image)

    # if l is longer than a.duration, may need to loop audio
    if ("audio" in values and len(values["audio"]) > 0):
        a = AudioFileClip(values["audio"])

    if ("length" in values):
        l = values["length"]
    elif (a != None):
        l = a.duration

    clip = ImageClip(numpy.array(image), duration=l)
    if (a != None):
        clip = clip.set_audio(a.subclip(0, l))
        if ("volume" in values):
            clip = clip.volumex(values["volume"])
    return clip

def create_resource(resource_options):
    if (resource_options["key"] == "combine"):
        return combine(resource_options["value"])
    elif (resource_options["key"] == "createimagevideo"):
        return create_image_video(resource_options["value"])

def process_scene(scene):
    resource = None

    if "resource" in scene:
        scene_resource = scene["resource"]
        if ("isFolder" in scene_resource and scene_resource["isFolder"]):
            return process_folder_scene(scene_resource)
        if "path" in scene_resource:
            resource = VideoFileClip(scene_resource["path"])
            if ("subclip" in scene_resource and scene_resource["subclip"]["enabled"]):
                resource = resource.subclip(scene_resource["subclip"]["start"], scene_resource["subclip"]["end"])
    elif "createresource" in scene:
        resource = create_resource(scene["createresource"])

    if "behaviors" in scene:
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
    print("Done building thumbnail")
    processor_settings = episode_data["video_processor"]
    clips = process_scenes(processor_settings)

    final_video = concatenate_videoclips(clips)
    final_video = behavior_intro(final_video, processor_settings.get("intro"))
    final_video = behavior_outro(final_video, processor_settings.get("outro"))
    print(final_video.duration / 60.0)
    output_format = episode_data["output_format"]
    output_path = output_format.format(**episode_data)
    final_video.write_videofile(output_path, threads = episode_data["threads"], fps=final_video.fps if final_video.fps != None else 120)

#upload_file = 'upload.json'
#if (len(sys.argv) > 1):
#    upload_file = sys.argv[1]

#options = get_options(upload_file)
#process_episode(options)
