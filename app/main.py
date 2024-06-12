import qrcode
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from PIL import Image
from io import BytesIO
from fastapi.responses import StreamingResponse
from aiomysql import create_pool

app = FastAPI()

# Database connection details
DB_HOST = "localhost"
DB_USER = "id22250032_sarvaiadmin"
DB_PASSWORD = "Bappa@21"
DB_NAME = "id22250032_sarvai"


async def validate_api_key(api_key: str):
    # Establish the database connection
    pool = await create_pool(host=DB_HOST, port=3306, user=DB_USER, password=DB_PASSWORD, db=DB_NAME)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT services FROM users WHERE api = %s", (api_key,))
            result = await cur.fetchone()
    pool.close()
    if result:
        allocated_services = result[0].split(',')
        if "QR Code Generator" in allocated_services:
            return True
    return False

@app.post("/generate_qr/")
async def generate_qr(
    api_key: str = Form(...),
    qr_data: str = Form(...),
    color: str = Form("#000000"),
    background: str = Form("#FFFFFF"),
    bg_img: UploadFile = File(None),
    embed_img: UploadFile = File(None)
):
    # Validate API key
    if not await validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key or service not allocated")


    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=color, back_color=background).convert("RGBA")

    if bg_img:
        bg_img_data = await bg_img.read()
        bg_img = Image.open(BytesIO(bg_img_data)).convert("RGBA")
        qr_img = qr_img.resize(bg_img.size)
        qr_img = Image.alpha_composite(bg_img, qr_img)

    if embed_img:
        embed_img_data = await embed_img.read()
        embed_img = Image.open(BytesIO(embed_img_data)).convert("RGBA")
        qr_size = qr_img.size[0]
        void_size = qr_size // 5
        embed_img.thumbnail((qr_size - void_size * 2, qr_size - void_size * 2))
        position = ((qr_img.size[0] - embed_img.size[0]) // 2, (qr_img.size[1] - embed_img.size[1]) // 2)
        qr_img.paste(embed_img, position, embed_img)

    img_byte_arr = BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")
