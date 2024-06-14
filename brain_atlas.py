import requests
from PIL import Image
from io import BytesIO
import os


def atlas_url(ml, ap, dv, kind="rat"):
    """
    Constructs the URL for the rat or mouse brain atlas API based on the provided coordinates.
    In neuroscience, ML, AP, and DV coordinates are commonly used to specify locations within 
    the brain. Here's what they stand for:

    Args:
    ML(float): Medio-lateral coordinate. It refers to the position along the medial-lateral axis of 
        the brain. The medio-lateral axis runs from the midline (medial) to the sides 
        (lateral) of the brain.
    AP(float): Antero-posterior coordinate. It refers to the position along the anterior-posterior 
        axis of the brain. The anterior-posterior axis runs from the front (anterior) to the
        back (posterior) of the brain.
    DV(float): Dorso-ventral coordinate. It refers to the position along the dorso-ventral axis of
        the brain. The dorso-ventral axis runs from the top (dorsal) to the bottom (ventral) 
        of the brain.
    Returns:
        str: The constructed URL.
    """
    if "ra" in kind.lower():
        api = "http://labs.gaidi.ca/rat-brain-atlas/api.php?"
        print(f"check the url: {api[:-8]}?ml={ml}&ap={ap}&dv={dv}")
    elif "mo" in kind.lower() or "mi" in kind.lower():
        api = "https://labs.gaidi.ca/mouse-brain-atlas/?"
    return f"{api}ml={ml}&ap={ap}&dv={dv}"


def get_3fpath(dir_save, ml, ap, dv):
    """
    Generates a filename based on the provided coordinates and directory.

    Args:
        dir_save (str): The directory where the file will be saved.
        ml (float): The ML coordinate.
        ap (float): The AP coordinate.
        dv (float): The DV coordinate.

    Returns:
        str: The generated filename.
    """
    filename, file_extension = os.path.splitext(dir_save)
    if file_extension == "":
        filename += f"brainatlas_ml={ml}&ap={ap}&dv={dv}"
    return filename


def download_image(image_url, color_mode=True):
    """
    Downloads an image from a given URL and converts it to RGB mode if required.

    Args:
        image_url (str): The URL of the image to download.
        color_mode (bool, optional): Whether to convert the image to RGB mode. Defaults to True.

    Returns:
        PIL.Image: The downloaded image.
    """
    try:
        # Download the image from the specified URL
        response = requests.get(image_url)

        # Check if the response status code is OK (200)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        if color_mode:
            image = image.convert("RGB")
        return image
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to download image from {image_url}")
        print(e)
        return None


def brain_atlas(ml, ap, dv, kind="rat", dir_save=None, pdf_filename=None):
    """
    Retrieves images of the rat or mouse brain atlas for the specified coordinates.

    Args:
        ml (float): The ML coordinate.
        ap (float): The AP coordinate.
        dv (float): The DV coordinate.
        kind (str, optional): The type of brain atlas ('rat' or 'mouse'). Defaults to 'rat'.
        dir_save (str, optional): The directory where the images will be saved. Defaults to None.

    Returns:
        tuple: A tuple containing PIL images of coronal, sagittal, and horizontal views, respectively.

    Note:
        The images are also saved as PDF files in the specified directory if `dir_save` is provided.
    """
    # Construct the URL for the rat brain atlas API based on the provided coordinates
    url = atlas_url(ml, ap, dv, kind=kind)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Download and process the images from the URLs provided in the JSON data
        coronal_image = download_image(data["coronal"]["image_url"], color_mode=True)
        sagittal_image = download_image(data["sagittal"]["image_url"], color_mode=True)
        horizontal_image = download_image(
            data["horizontal"]["image_url"], color_mode=True
        )

        # Check if all images were successfully downloaded
        if coronal_image and sagittal_image and horizontal_image:
            if dir_save:
                # Construct filename with kind suffix
                filename = get_3fpath(dir_save, ml, ap, dv)
                coronal_image.save(filename + f"_{kind}_coronal.pdf")
                sagittal_image.save(filename + f"_{kind}_sagittal.pdf")
                horizontal_image.save(filename + f"_{kind}_horizontal.pdf")
            return (coronal_image, sagittal_image, horizontal_image)
        else:
            print("Error: Unable to download images.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to complete web request\n{url}.")
        print(e)
        return None


# # Example usage:
# ml = 8.64
# ap = -0.36
# dv = 7.0

# # Retrieve the rat brain atlas images for the specified coordinates
# S = brain_atlas(
#     ml, ap, dv, dir_save="/Users/macjianfeng/Dropbox/Downloads/", kind="rat"
# )

# if S:
#     # Display or further process the retrieved images
#     coronal_image = S["coronal"]
#     sagittal_image = S["sagittal"]
#     horizontal_image = S["horizontal"]
#     # coronal_image.show()  # Display the coronal image
#     # Similarly, you can display or process sagittal and horizontal images