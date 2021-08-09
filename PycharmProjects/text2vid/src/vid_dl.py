import requests
import random
import os


def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path


def download_vid(kw, save_dir):
    api_key = '563492ad6f9170000100000100109c3d9f2244abb9cd836df982292d'
    for key in kw:
        try:
            search_videos = f'https://api.pexels.com/videos/search?query={key}&per_page=10'
            req = requests.get(search_videos, timeout=15, headers={"Authorization": api_key})
            video_list = list(req.json()['videos'])
            vid = random.sample(video_list, 1)[0]

            counter = 0
            while True:
                # TODO: Give options for different orientations
                if vid['width'] > vid['height']:  # look for horizontal orientation videos
                    url_video = f"https://www.pexels.com/video/{vid['id']}/download"
                    r = requests.get(url_video)

                    path = uniquify(os.path.join(save_dir, f"{key}.mp4"))
                    with open(path, 'wb') as outfile:
                        outfile.write(r.content)
                    counter += 1
                    break
                else:
                    counter += 1
                    if counter == 10:
                        break
                    else:
                        pass
        except ValueError:
            pass
