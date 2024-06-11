import qrcode
from fastapi import FastAPI, File, Form, UploadFile
from PIL import Image
from io import BytesIO
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/generate_qr/")
async def generate_qr(
    qr_data: str = Form("aaa"),
    color: str = Form("#000000"),
    background: str = Form("#FFFFFF"),
    bg_img: UploadFile = File(None),
    embed_img: UploadFile = File(None)
):
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
