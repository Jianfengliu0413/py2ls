import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from PIL import Image
from skimage import filters, morphology, measure, color

#  用来处理ich图像的初级工具包


def open_img(dir_img, convert="gray", plot=False):
    # Step 1: Load the image
    image = Image.open(dir_img)

    if convert == "gray" or convert == "grey":
        gray_image = image.convert("L")
        image_array = np.array(gray_image)
    else:
        image_array = np.array(image)
    if plot:
        _, axs = plt.subplots(1, 2)
        axs[0].imshow(image)
        axs[1].imshow(image_array)
        axs[0].set_title("img_raw")
        axs[1].set_title(f"img_{convert}")
    return image, image_array


from skimage import filters, morphology


def clean_img(
    img,
    method=["threshold_otsu", "objects", "holes"],
    obj_min=50,
    hole_min=50,
    filter=None,
    plot=False,
    cmap="grey",
):
    if isinstance(method, str):
        if method == "all":
            method = ["threshold_otsu", "objects", "holes"]
        else:
            method = [method]
    if any("thr" in met or "ot" in met for met in method) and filter is None:
        thr_otsu = filters.threshold_otsu(img)
        img_update = img > thr_otsu
    if any("obj" in met for met in method):
        img_update = morphology.remove_small_objects(img_update, min_size=obj_min)
    if any("hol" in met for met in method):
        img_update = morphology.remove_small_holes(img_update, area_threshold=hole_min)
    if ("thr" in met for met in method) and filter:  # threshold
        mask = (img >= filter[0]) & (img <= filter[1])
        img_update = np.where(mask, img, 0)

    if plot:
        plt.imshow(img_update, cmap=cmap)
    return img_update


from skimage import filters, segmentation


def segment_img(
    img,
    filter=[30, 150],
    plot=False,
    mode="reflect",  # 'reflect' or 'constant'
    method="region",  # 'region' or 'edge', 'threshold'
    area_min=50,
    cmap="jet",
    connectivity=1,
    output="segmentation",
):
    if "reg" in method:  # region method
        # 1. find an elevation map using the Sobel gradient of the image
        elevation_map = filters.sobel(img, mode=mode)
        # 2. find markers of the background and the coins based on the extreme parts of the histogram of gray values.
        markers = np.zeros_like(img)
        # Apply filtering based on provided filter values
        if filter is not None:
            markers[img < filter[0]] = 1
            markers[img > filter[1]] = 2
        else:
            # If no filter is provided, set markers across the whole range of the image
            markers[img == img.min()] = 1
            markers[img == img.max()] = 2
        # 3. watershed transform to fill regions of the elevation map starting from the markers
        img_segmentation = segmentation.watershed(
            elevation_map, markers=markers, connectivity=connectivity
        )
        if plot:
            _, axs = plt.subplots(2, 2)
            for i, ax in enumerate(axs.flatten().tolist()):
                if i == 0:
                    ax.imshow(img)
                    ax.set_title("image")
                elif i == 1:
                    ax.imshow(elevation_map, cmap=cmap)
                    ax.set_title("elevation map")
                elif i == 2:
                    ax.imshow(markers, cmap=cmap)
                    ax.set_title("markers")
                elif i == 3:
                    ax.imshow(img_segmentation, cmap=cmap)
                    ax.set_title("segmentation")
                ax.set_axis_off()
        if "el" in output:
            return elevation_map
        elif "mar" in output:
            return markers
        elif "seg" in output:
            return img_segmentation
        else:
            return img_segmentation
    elif "ed" in method:  # edge
        edges = cal_edges(img)
        fills = fill_holes(edges)
        img_segmentation = remove_holes(fills, area_min)
        if plot:
            _, axs = plt.subplots(2, 2)
            for i, ax in enumerate(axs.flatten().tolist()):
                if i == 0:
                    ax.imshow(img)
                    ax.set_title("image")
                elif i == 1:
                    ax.imshow(edges, cmap=cmap)
                    ax.set_title("edges map")
                elif i == 2:
                    ax.imshow(fills, cmap=cmap)
                    ax.set_title("fills")
                elif i == 3:
                    ax.imshow(img_segmentation, cmap=cmap)
                    ax.set_title("segmentation")
                ax.set_axis_off()
        if "seg" in output:
            return img_segmentation
        elif "ed" in output:
            return edges
        elif "fill" in output:
            return fills
        else:
            return img_segmentation
    elif "thr" in method:  # threshold
        if filter:
            mask = (img >= filter[0]) & (img <= filter[1])
            img_threshold = np.where(mask, img, 0)
            if plot:
                plt.imshow(img_threshold, cmap=cmap)
            return img_threshold
        else:
            return None


from skimage import measure


def label_img(img, plot=False):
    img_label = measure.label(img)
    if plot:
        plt.imshow(img_label)
    return img_label


def img_process(img, **kwargs):
    convert = "gray"
    method_clean_img = ["threshold_otsu", "objects", "holes"]
    obj_min_clean_img = 50
    hole_min_clean_img = 50
    plot = True
    for k, v in kwargs.items():
        if "convert" in k.lower():
            convert = v
        if "met" in k.lower() and any(
            ["clean" in k.lower(), "rem" in k.lower(), "rm" in k.lower()]
        ):
            method_clean_img = v
        if "obj" in k.lower() and any(
            ["clean" in k.lower(), "rem" in k.lower(), "rm" in k.lower()]
        ):
            obj_min_clean_img = v
        if "hol" in k.lower() and any(
            ["clean" in k.lower(), "rem" in k.lower(), "rm" in k.lower()]
        ):
            hole_min_clean_img = v
        if "plot" in k.lower():
            plot = v

    if isinstance(img, str):
        image, image_array = open_img(img, convert=convert)
        normalized_image = image_array / 255.0
    else:
        cleaned_image = img
        image_array = cleaned_image
        normalized_image = cleaned_image
        image = cleaned_image

    # Remove small objects and fill small holes
    cleaned_image = clean_img(
        img=image_array,
        method=method_clean_img,
        obj_min=obj_min_clean_img,
        hole_min=hole_min_clean_img,
        plot=False,
    )
    # Label the regions
    label_image = label_img(cleaned_image)
    overlay_image = overlay_imgs(label_image, image=image_array)
    regions = measure.regionprops(label_image, intensity_image=image_array)
    region_props = measure.regionprops_table(
        label_image, intensity_image=image_array, properties=props_list
    )
    df_regions = pd.DataFrame(region_props)
    # Pack the results into a single output variable (dictionary)
    output = {
        "img": image,
        "img_array": image_array,
        "img_scale": normalized_image,
        "img_clean": cleaned_image,
        "img_label": label_image,
        "img_overlay": overlay_image,
        "regions": regions,
        "df_regions": df_regions,
    }
    if plot:
        imgs = []
        [imgs.append(i) for i in list(output.keys()) if "img" in i]
        for img_ in imgs:
            plt.figure()
            plt.imshow(output[img_])
            plt.title(img_)
    return output


# def img_preprocess(dir_img, subtract_background=True, size_obj=50, size_hole=50,**kwargs):
#     """
#     Processes an image by performing thresholding, morphological operations,
#     and region labeling.

#     Parameters:
#     - dir_img: Path to the image file.
#     - size_obj: Minimum size of objects to keep (default: 50).
#     - size_hole: Maximum size of holes to fill (default: 50).

#     Returns:
#     - output: Dictionary containing the overlay image, threshold value, and regions.
#     """
#     props_list = [
#         "area",  # Number of pixels in the region. Useful for determining the size of regions.
#         "area_bbox",
#         "area_convex",
#         "area_filled",
#         "axis_major_length",  # Lengths of the major and minor axes of the ellipse that fits the region. Useful for understanding the shape's elongation and orientation.
#         "axis_minor_length",
#         "bbox",  # Bounding box coordinates (min_row, min_col, max_row, max_col). Useful for spatial localization of regions.
#         "centroid",  # Center of mass coordinates (centroid-0, centroid-1). Helps locate the center of each region.
#         "centroid_local",
#         "centroid_weighted",
#         "centroid_weighted_local",
#         "coords",
#         "eccentricity",  # Measure of how elongated the region is. Values range from 0 (circular) to 1 (line). Useful for assessing the shape of regions.
#         "equivalent_diameter_area",  # Diameter of a circle with the same area as the region. Provides a simple measure of size.
#         "euler_number",
#         "extent",  # Ratio of the region's area to the area of its bounding box. Indicates how much of the bounding box is filled by the region.
#         "feret_diameter_max",  # Maximum diameter of the region, providing another measure of size.
#         "image",
#         "image_convex",
#         "image_filled",
#         "image_intensity",
#         "inertia_tensor",  # ensor describing the distribution of mass in the region, useful for more advanced shape analysis.
#         "inertia_tensor_eigvals",
#         "intensity_max",  # Maximum intensity value within the region. Helps identify regions with high-intensity features.
#         "intensity_mean",  # Average intensity value within the region. Useful for distinguishing between regions based on their brightness.
#         "intensity_min",  # Minimum intensity value within the region. Useful for regions with varying intensity.
#         "intensity_std",
#         "label",  # Unique identifier for each region.
#         "moments",
#         "moments_central",
#         "moments_hu",  # Hu moments are a set of seven invariant features that describe the shape of the region. Useful for shape recognition and classification.
#         "moments_normalized",
#         "moments_weighted",
#         "moments_weighted_central",
#         "moments_weighted_hu",
#         "moments_weighted_normalized",
#         "orientation",  # ngle of the major axis of the ellipse that fits the region. Useful for determining the orientation of elongated regions.
#         "perimeter",  # Length of the boundary of the region. Useful for shape analysis.
#         "perimeter_crofton",
#         "slice",
#         "solidity",  # Ratio of the area of the region to the area of its convex hull. Indicates how solid or compact a region is.
#     ]
#     if isinstance(dir_img, str):
#         # Step 1: Load the image
#         image = Image.open(dir_img)

#         # Step 2: Convert the image to grayscale and normalize
#         gray_image = image.convert("L")
#         image_array = np.array(gray_image)
#         normalized_image = image_array / 255.0
#     else:
#         cleaned_image = dir_img
#         image_array = cleaned_image
#         normalized_image = cleaned_image
#         image = cleaned_image
#         binary_image = cleaned_image
#         thr_val = None
#     if subtract_background:
#         # Step 3: Apply thresholding to segment the image
#         thr_val = filters.threshold_otsu(image_array)
#         print(f"Threshold value is: {thr_val}")

#         # Apply thresholds and generate binary images
#         binary_image = image_array > thr_val

#         # Step 4: Perform morphological operations to clean the image
#         # Remove small objects and fill small holes
#         cleaned_image_rm_min_obj = morphology.remove_small_objects(
#             binary_image, min_size=size_obj
#         )
#         cleaned_image = morphology.remove_small_holes(
#             cleaned_image_rm_min_obj, area_threshold=size_hole
#         )

#     # Label the regions
#     label_image = label_img(cleaned_image)

#     # Optional: Overlay labels on the original image
#     overlay_image = color.label2rgb(label_image, image_array)
#     regions = measure.regionprops(label_image, intensity_image=image_array)
#     region_props = measure.regionprops_table(
#         label_image, intensity_image=image_array, properties=props_list
#     )
#     df_regions = pd.DataFrame(region_props)
#     # Pack the results into a single output variable (dictionary)
#     output = {
#         "img": image,
#         "img_array": image_array,
#         "img_scale": normalized_image,
#         "img_binary": binary_image,
#         "img_clean": cleaned_image,
#         "img_label": label_image,
#         "img_overlay": overlay_image,
#         "thr_val": thr_val,
#         "regions": regions,
#         "df_regions": df_regions,
#     }

#     return output


def cal_pearson(img1, img2):
    """Compute Pearson correlation coefficient between two images."""
    img1_flat = img1.flatten()
    img2_flat = img2.flatten()
    r, p = pearsonr(img1_flat, img2_flat)
    return r, p


def cal_manders(img1, img2):
    """Compute Manders' overlap coefficient between two binary images."""
    img1_binary = img1 > filters.threshold_otsu(img1)
    img2_binary = img2 > filters.threshold_otsu(img2)
    overlap_coef = np.sum(img1_binary & img2_binary) / np.sum(img1_binary)
    return overlap_coef


def overlay_imgs(
    *imgs,
    image=None,
    colors=None,
    alpha=0.3,
    bg_label=0,
    bg_color=(0, 0, 0),
    image_alpha=1,
    kind="overlay",
    saturation=0,
    channel_axis=-1,
):
    # Ensure all input images have the same shape
    print(
        f'\nusage:\nich2ls.overlay_imgs(res_b["img_binary"], res_r["img_binary"], bg_label=0)'
    )
    shapes = [img.shape for img in imgs]
    if not all(shape == shapes[0] for shape in shapes):
        raise ValueError("All input images must have the same shape")

    # If no image is provided, use the first input image as the base
    if image is None:
        image = imgs[0]

    # Combine the images into a label, with unique multipliers for each image
    label = sum((img.astype(np.uint) * (i + 1) for i, img in enumerate(imgs)))

    # Create the overlay image
    overlay_image = color.label2rgb(
        label,
        image=image,
        bg_label=bg_label,
        colors=colors,
        alpha=alpha,
        bg_color=bg_color,
        image_alpha=image_alpha,
        saturation=saturation,
        kind=kind,
        channel_axis=channel_axis,  # Corrected from saturation to channel_axis
    )

    return overlay_image


from skimage import exposure


# Comparing edge-based and region-based segmentation
def draw_hist(img, ax=None, **kwargs):
    """
    _, axs = plt.subplots(1, 2)
    draw_hist(image, c="r", ax=axs[1], lw=2, ls=":")
    """
    print(f"img type: {type(img)}")
    if not isinstance(img, np.ndarray):
        img = np.array(img)
    hist, hist_centers = exposure.histogram(img)
    if ax is None:
        ax = plt.gca()
    ax.plot(hist_centers, hist, **kwargs)


from skimage import feature


# delineate the contours of the coins using edge-based segmentation
def cal_edges(img, plot=False, cmap=plt.cm.gray):
    edges = feature.canny(img)
    if plot:
        plt.imshow(edges, cmap=cmap)
    return edges


from scipy import ndimage as ndi


# These contours are then filled using mathematical morphology.
def fill_holes(img, plot=False):
    img_fill_holes = ndi.binary_fill_holes(img)
    if plot:
        plt.imshow(img_fill_holes, cmap=plt.cm.gray)
    return img_fill_holes


from skimage import morphology


def remove_holes(img, size=50, plot=False):
    img_rm_holes = morphology.remove_small_objects(img, size)
    if plot:
        plt.imshow(img_rm_holes, cmap=plt.cm.gray)
    return img_rm_holes


import matplotlib.patches as mpatches
from skimage import measure, color


def draw_bbox(
    img,
    df=None,
    img_label=None,
    img_label2rgb=None,
    show=True,  # plot the image
    bg_alpha=1,  # the alpha of the bg image
    area_min=1,
    area_max=None,
    fill=False,
    edgecolor="red",
    linewidth=2,
    ax=None,
    **kwargs,
):
    """
    ich2ls.draw_bbox(
    res["img_label"], fill=False, color="r", lw=1, edgecolor="w", alpha=0.4)
    """
    if ax is None:
        ax = plt.gca()
    if img_label is None:
        img_label = measure.label(img)
    if isinstance(show, bool):
        if show:
            if img_label2rgb is None:
                img_label2rgb = color.label2rgb(img_label, image=img, bg_label=0)
            ax.imshow(img_label2rgb, alpha=bg_alpha)
    elif isinstance(show, str):
        if "raw" in show:
            ax.imshow(img, alpha=bg_alpha)
        elif "label" in show:
            ax.imshow(img_label, alpha=bg_alpha)
        elif "rgb" in show:
            if img_label2rgb is None:
                img_label2rgb = color.label2rgb(img_label, image=img, bg_label=0)
            ax.imshow(img_label2rgb, alpha=bg_alpha)
        elif "no" in show.lower():
            pass
    num = 0
    if df is None:
        for region in measure.regionprops(img_label):
            # take regions with large enough areas
            if area_max is None:
                area_max = np.inf
            if area_min <= region.area <= area_max:
                minr, minc, maxr, maxc = region.bbox
                rect = mpatches.Rectangle(
                    (minc, minr),
                    maxc - minc,
                    maxr - minr,
                    fill=fill,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                    **kwargs,
                )
                ax.add_patch(rect)
                num += 1
    else:
        # Iterate over each row in the DataFrame and draw the bounding boxes
        for _, row in df.iterrows():
            minr = row["bbox-0"]
            minc = row["bbox-1"]
            maxr = row["bbox-2"]
            maxc = row["bbox-3"]

            # Optionally filter by area if needed
            area = (maxr - minr) * (maxc - minc)
            if area >= area_min:
                rect = mpatches.Rectangle(
                    (minc, minr),
                    maxc - minc,
                    maxr - minr,
                    fill=fill,
                    edgecolor=edgecolor,
                    linewidth=linewidth,
                    **kwargs,
                )
                ax.add_patch(rect)
                num += 1
    return num


props_list = [
    "area",  # Number of pixels in the region. Useful for determining the size of regions.
    "area_bbox",
    "area_convex",
    "area_filled",
    "axis_major_length",  # Lengths of the major and minor axes of the ellipse that fits the region. Useful for understanding the shape's elongation and orientation.
    "axis_minor_length",
    "bbox",  # Bounding box coordinates (min_row, min_col, max_row, max_col). Useful for spatial localization of regions.
    "centroid",  # Center of mass coordinates (centroid-0, centroid-1). Helps locate the center of each region.
    "centroid_local",
    "centroid_weighted",
    "centroid_weighted_local",
    "coords",
    "eccentricity",  # Measure of how elongated the region is. Values range from 0 (circular) to 1 (line). Useful for assessing the shape of regions.
    "equivalent_diameter_area",  # Diameter of a circle with the same area as the region. Provides a simple measure of size.
    "euler_number",
    "extent",  # Ratio of the region's area to the area of its bounding box. Indicates how much of the bounding box is filled by the region.
    "feret_diameter_max",  # Maximum diameter of the region, providing another measure of size.
    "image",
    "image_convex",
    "image_filled",
    "image_intensity",
    "inertia_tensor",  # ensor describing the distribution of mass in the region, useful for more advanced shape analysis.
    "inertia_tensor_eigvals",
    "intensity_max",  # Maximum intensity value within the region. Helps identify regions with high-intensity features.
    "intensity_mean",  # Average intensity value within the region. Useful for distinguishing between regions based on their brightness.
    "intensity_min",  # Minimum intensity value within the region. Useful for regions with varying intensity.
    "intensity_std",
    "label",  # Unique identifier for each region.
    "moments",
    "moments_central",
    "moments_hu",  # Hu moments are a set of seven invariant features that describe the shape of the region. Useful for shape recognition and classification.
    "moments_normalized",
    "moments_weighted",
    "moments_weighted_central",
    "moments_weighted_hu",
    "moments_weighted_normalized",
    "orientation",  # ngle of the major axis of the ellipse that fits the region. Useful for determining the orientation of elongated regions.
    "perimeter",  # Length of the boundary of the region. Useful for shape analysis.
    "perimeter_crofton",
    "slice",
    "solidity",  # Ratio of the area of the region to the area of its convex hull. Indicates how solid or compact a region is.
]
