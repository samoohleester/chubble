import os
from pathlib import Path
from PIL import Image, ImageFile

# Force PIL to load truncated/partially corrupted images without throwing an error
ImageFile.LOAD_TRUNCATED_IMAGES = True


png_counter = 0
jpg_counter = 0
pdf_counter = 0
other_counter = 0

def identify_and_check_file(dat_file_path: Path) -> str:
    global pdf_counter, png_counter, jpg_counter, other_counter

    with open(dat_file_path, "rb") as f:
        header = f.read(16)

    if header.startswith(b"\x89PNG"):
        file_type = "PNG Image"
        png_counter += 1
    elif header.startswith(b"\xff\xd8\xff"):
        file_type = "JPEG Image"
        jpg_counter += 1
    elif header.startswith(b"%PDF"):
        file_type = "PDF Document"
        pdf_counter += 1
    else:
        file_type = f"Text / Other Binary (Header: {header})"

    return file_type

def reconstruct_png_file(png_path: Path, dest_path: str):
    og_name = png_path.stem
    with Image.open(png_path) as img:
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        dest_path = dest_path / f"{og_name}.png"

        img.save(dest_path, format="PNG")

def save_dat_as_pdf(pdf_path: Path, dest_path: str):
    dest_path = dest_path / f"{pdf_path.stem}.pdf"
    with open(pdf_path, "rb") as f_in:
        pdf_bytes = f_in.read()

    with open(dest_path, "wb") as f_out:
        f_out.write(pdf_bytes)

    

def reconstruct_file(image_paths: list[Path]):
    # script_dir = Path(__file__).resolve().parent
    dest_path = Path("chat_attachments")
    dest_path.mkdir(exist_ok=True)


    for index, input_file in enumerate(image_paths, start=1):
        if not input_file.exists():
            print(f"Skipping: File '{input_file}' not found.")
            continue
        try:
            file_type = identify_and_check_file(input_file)

            if file_type == "PNG Image":
                destination_path = dest_path / "png_images"
                destination_path.mkdir(parents=True, exist_ok=True)
                reconstruct_png_file(input_file, destination_path)

            elif file_type == "PDF Document":
                destination_path = dest_path / "pdf_files"
                destination_path.mkdir(parents=True, exist_ok=True)
                save_dat_as_pdf(input_file, destination_path)
                

        except Exception as e:
            print(f"[{index}] Error processing '{input_file}': {e}")


if __name__ == "__main__":
    all_dats_path = Path(
        r"C:\Users\thisi\OneDrive\Desktop\chatgpt visualizer\35b5640b80ad48e517ce4d0ee8528aa788f27ca1bbd8291336841f8c716ad49c-2026-09-03-01-28-56-4ed77695f5a84fc3be6abe71d7ab7790"
    )

    dat_files = [
        f for f in all_dats_path.iterdir() 
        if f.is_file() and f.suffix.lower() == ".dat"
    ]
    
    reconstruct_file(dat_files)
    print(f"PNG Count: {png_counter}\nJPEG Count: {jpg_counter}\nPDF Count: {pdf_counter}\n Other Count: {other_counter}")