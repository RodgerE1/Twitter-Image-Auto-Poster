import os


def list_image_files(directory):
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    image_files = [
        f
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
        and any(f.lower().endswith(ext) for ext in image_extensions)
    ]
    return image_files


def main():
    current_directory = os.getcwd()
    image_files = list_image_files(current_directory)
    if not image_files:
        print("No files found")
    else:
        for idx, image_file in enumerate(image_files, 1):
            print(f"{idx}. {image_file}")


if __name__ == "__main__":
    main()
