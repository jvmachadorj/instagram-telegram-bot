image = None


def post_on_instagram(instagram_bot):
    global image

    # Upload Photo
    instagram_bot.uploadPhoto(image.path, caption=image.caption, upload_id=None)
    print("Posted with caption {}".format(image.caption))
