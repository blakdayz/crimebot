from fastapi import FastAPI, File, UploadFile, HTTPException
import requests
import os
import configparser
config = configparser.ConfigParser()
config.read("deepfake.ini")
REMOTE_SERVER_ADDRESS = config.get("Server", "host")
app = FastAPI()



# Replace <linux-ip> with the actual IP address of your Linux machine
DEEPFAKE_SERVER_URL = f"http://{REMOTE_SERVER_ADDRESS}:8080"

@app.post("/generate_deepfake")
async def generate_deepfake(source_file: UploadFile = File(...), target_file: UploadFile = File(...)):
    """
    Sends a seed (source) image we wish to clone to realtime deep fake AI server running at the location above.
    :param source_file:
    :param target_file:
    :return:
    """
    if source_file.content_type not in ['image/jpeg', 'video/mp4']:
        raise HTTPException(status_code=400, detail="Only JPEG images and MP4 videos are supported for source.")
    if target_file.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are supported for target.")

    try:
        # Save source file to a temporary location
        source_path = os.path.join("/tmp", f"source_{os.getpid()}.{source_file.filename.split('.')[-1]}")
        with open(source_path, "wb") as buffer:
            await source_file.readinto(buffer)

        # Save target file to a temporary location
        target_path = os.path.join("/tmp", f"target_{os.getpid()}.{target_file.filename.split('.')[-1]}")
        with open(target_path, "wb") as buffer:
            await target_file.readinto(buffer)

        # Prepare the request payload
        files = {
            "source": ("source.jpg", open(source_path, "rb"), source_file.content_type),
            "target": ("target.png", open(target_path, "rb"), target_file.content_type)
        }

        # Send the request to DeepFakeLive server
        response = requests.post(
            f"{DEEPFAKE_SERVER_URL}/generate",
            files=files
        )
        response.raise_for_status()
        data = response.json()

        # Clean up temporary files
        os.remove(source_path)
        os.remove(target_path)

        # Return the generated deepfake file URL
        return {"deepfake_url": data.get("file_url")}

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error generating deepfake: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
