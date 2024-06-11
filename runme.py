import qrcode
from PIL import Image

def create_custom_qr(data, color="#000000", background="#FFFFFF", bg_img_path=None, embed_image_path=None, qr_path='custom_qr.png'):
    if bg_img_path:
        # Load the base image
        base_img = Image.open(bg_img_path).convert("RGBA")
        img_w, img_h = base_img.size
        
        # Calculate the average brightness of the image
        # (This part is commented out since it's not necessary for the specified modifications)
        
        # Set QR code color based on brightness if not provided
        qr_color = color
        
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create the QR code image
        qr_img = qr.make_image(fill_color=qr_color, back_color="transparent").convert("RGBA")
        qr_img = qr_img.resize((img_w, img_h))

        # Adjust QR code colors based on the base image
        # (This part is commented out since it's not necessary for the specified modifications)

        # Composite the QR code onto the image
        combined_img = Image.alpha_composite(base_img, qr_img)
    else:
        # Generate the QR code with specified colors
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create the QR code image using specified colors
        qr_img = qr.make_image(fill_color=color, back_color=background).convert("RGBA")
        combined_img = qr_img

    # Embed image in the center of the QR code if provided
    if embed_image_path:
        embed_image = Image.open(embed_image_path).convert("RGBA")
        qr_width, qr_height = qr_img.size
        max_size = min(qr_width, qr_height) // 5
        embed_image = embed_image.resize((max_size, max_size))
        embed_image_width, embed_image_height = embed_image.size
        position = ((qr_width - embed_image_width) // 2, (qr_height - embed_image_height) // 2)
        combined_img.paste(embed_image, position)

    # Save the final image
    combined_img.save(qr_path)
    print(f"Custom QR code saved as {qr_path}")

if __name__ == "__main__":
    data = input("Enter the data for the QR code: ")
    color = input("Enter the hex color for the QR code (default is #000000): ") or "#000000"
    background = input("Enter the hex background color for the QR code (default is #FFFFFF): ") or "#FFFFFF"
    bg_img_path = input("Enter the path of the background image (or leave blank): ")
    embed_image_path = input("Enter the path of the image to embed in the QR code (or leave blank): ")
    qr_path = input("Enter the output file path (default is 'custom_qr.png'): ") or 'custom_qr.png'

    create_custom_qr(data, color, background, bg_img_path or None, embed_image_path or None, qr_path)
