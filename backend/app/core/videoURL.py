# import boto3
# from fastapi import HTTPException
# from botocore.exceptions import ClientError
# from app.utils.config import ENV_PROJECT


# AWS_ACCESS_KEY = ENV_PROJECT.AWS_ACCESS_KEY_ID
# AWS_SECRET_KEY = ENV_PROJECT.AWS_SECRET_ACCESS_KEY
# AWS_REGION = ENV_PROJECT.AWS_REGION

# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=AWS_ACCESS_KEY,
#     aws_secret_access_key=AWS_SECRET_KEY,
#     region_name=AWS_REGION,
# )


# async def get_video_url(category):
#     """
#     Return direct public video URLs instead of presigned URLs.
#     """
#     try:
#         base_url = "https://iivfstrgaiac01.blob.core.windows.net/iivf-chatbot-videos/"

#         video_urls = []
#         if category == "doctor":
#             video_keys = ENV_PROJECT.DOCTOR_TESTIMONIAL_VIDEOKEY
#             thumbnails=ENV_PROJECT.DOCTOR_TESTIMONIAL_THUMBNAIL
#             headings=ENV_PROJECT.DOCTOR_HEADING
#         elif category =="success_rate":
#             video_keys=ENV_PROJECT.SUCCESS_RATE_VIDEOKEY
#             thumbnails=ENV_PROJECT.SUCCESS_RATE_THUMBNAIL
#             headings=ENV_PROJECT.SUCCESS_HEADING
#         elif category=="cost_and_package":
#             video_keys=ENV_PROJECT.IVF_COST_VIDEOKEY
#             thumbnails=ENV_PROJECT.IVF_COST_THUMBNAIL
#             headings=ENV_PROJECT.COST_HEADING
#         elif category=="understanding_ivf":
#             video_keys=ENV_PROJECT.IVF_INFORMATION_VIDEOKEY
#             thumbnails=ENV_PROJECT.IVF_INFORMATION_THUMBNAIL
#             headings=ENV_PROJECT.IVF_INFORMATION_HEADING

#         else:
#             video_keys = ENV_PROJECT.PATIENT_TESTIMONIAL_VIDEOKEY
#             thumbnails=ENV_PROJECT.PATIENT_TESTIMONIAL_THUMBNAIL
#             headings=ENV_PROJECT.PATIENT_HEADING
#         for key, thumbnail,heading in zip(video_keys, thumbnails,headings):
#             url = f"{base_url}{key}"
#             thumb_url = f"{base_url}{thumbnail}"
#             description=key.split("/")[-1].replace(".mp4", "")

#             video_urls.append({
#                 "video_url": url,
#                 "thumbnail_url": thumb_url,
#                 "heading":heading,
#                 "description":description
#             })

#         return {"video_url": video_urls}

#     except Exception as e:
#         print("Error in get_video_url:", e)
#         return {"video_url": []}

from app.schemas.videos import Languages, VideoCategory
from app.models.videos import Video


LANGUAGE_MAP = {
    "English": Languages.ENGLISH,
    "हिन्दी": Languages.HINDI,
    "मराठी": Languages.MARATHI,
    "ગુજરાતી": Languages.GUJARATI,
    "ಕನ್ನಡ": Languages.KANADA,
    "বাংলা": Languages.BENGALI,
    "தமிழ்": Languages.TAMIL,
    "ਪੰਜਾਬੀ": Languages.PUNJABI,
    "অসমীয়া": Languages.ASSAMESE,
    "ଓଡ଼ିଆ": Languages.ODIA,
    "తెలుగు": Languages.TELUGU,
}


async def get_video_url(category: str, language_name: str):
    """
    Fetch videos from MongoDB based on category and human-readable language.
    Returns video URLs with heading & description.
    """
    try:
        base_url = "https://iivfstrgaiac01.blob.core.windows.net/iivf-chatbot-videos/"

        # Convert human-readable language to enum
        language_enum = LANGUAGE_MAP.get(language_name)
        if not language_enum:
            # fallback if language not found
            return {"video_url": []}

        # Fetch videos from MongoDB
        videos = await Video.find(
            Video.video_category == category, Video.language == language_enum.value
        ).to_list()

        if language_enum in [
            Languages.ENGLISH,
            Languages.PUNJABI,
            Languages.GUJARATI,
            Languages.ASSAMESE,
        ]:
            language_enum = Languages.HINDI

        video_urls = []
        for video in videos:
            url = f"{base_url}{video.video_category.value}/{language_enum.value}/{video.video_category.value}{video.video_number}.mp4"
            thumb_url = f"{base_url}{video.video_category.value}/thumbnail/{video.video_thumbnail}"

            video_urls.append(
                {
                    "video_url": url,
                    "thumbnail_url": thumb_url,
                    "heading": video.video_heading,
                    "description": video.video_description,
                }
            )
        return {"video_url": video_urls}

    except Exception as e:
        return {"video_url": []}
