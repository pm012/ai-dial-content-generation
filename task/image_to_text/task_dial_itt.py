import asyncio
#import os
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = 'dialx-banner.png'
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = 'image/png'
    
    #  1. Create DialBucketClient
    async with DialBucketClient(
        api_key=API_KEY,
        base_url=DIAL_URL
    ) as bucket_client:
    #  2. Open image file
    #  3. Use BytesIO to load bytes of image
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
    #  4. Upload file with client
        upload_response = await bucket_client.put_file(
            content=BytesIO(image_bytes),
            name=file_name,
            mime_type=mime_type_png
        )
    
    #  5. Return Attachment object with title (file name), url and type (mime type)
    return Attachment(
        title=file_name,
        url=upload_response.get("url"),
        type=mime_type_png
    )


def start() -> None:
    
    #  1. Create DialModelClient
    client = DialModelClient(
        api_key=API_KEY,
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name="gemini-2.5-pro"  # "gpt-4o", "gemini-2.5-pro", "anthropic.claude-v3-5-haiku" -not working (access deined)
    )
    #  2. Upload image (use `_put_image` method )
    attachment = asyncio.run(_put_image())
    #  3. Print attachment to see result
    print(attachment)
    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])
    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis
    client.get_completion(
        [
            Message(
                role=Role.USER,
                content="What do you see on this picture?",
                custom_content=CustomContent(
                    attachments=[attachment]
                )
            )
        ]
    )
    


start()
