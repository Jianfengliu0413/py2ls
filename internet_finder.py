from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse, urljoin
import base64
import pandas as pd
from collections import Counter
import random
import logging
from time import sleep
import stem.process
from stem import Signal
from stem.control import Controller
import json
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define supported content types and corresponding parsers
CONTENT_PARSERS = {
    "text/html": lambda text, parser: BeautifulSoup(text, parser),
    "application/json": lambda text, parser: json.loads(text),
    "text/xml": lambda text, parser: BeautifulSoup(text, parser),
    "text/plain": lambda text, parser: text.text,
}

def fetch_all(url, parser="lxml"): # lxml is faster, # parser="html.parser"
    try:
        # Generate a random user-agent string
        headers = {"User-Agent": user_agent()}

        # Send the initial request
        response = requests.get(url, headers=headers)

        # If the response is a redirect, follow it
        while response.is_redirect:
            logger.info(f"Redirecting to: {response.headers['Location']}")
            response = requests.get(response.headers["Location"], headers=headers)
        # Check for a 403 error
        if response.status_code == 403:
            logger.warning("403 Forbidden error. Retrying...")
            # Retry the request after a short delay
            sleep(random.uniform(1, 3))
            response = requests.get(url, headers=headers)
            # Raise an error if retry also fails
            response.raise_for_status()

        # Raise an error for other HTTP status codes
        response.raise_for_status()

        # Get the content type
        content_type = response.headers.get("content-type", "").split(";")[0].lower()
        content = response.content.decode(response.encoding)
        # logger.info(f"Content type: {content_type}")

        # Check if content type is supported
        if content_type in CONTENT_PARSERS:
            return content_type, CONTENT_PARSERS[content_type](content, parser)
        else:
            logger.warning("Unsupported content type")
            return None, None
    except requests.RequestException as e:
        logger.error(f"Error fetching URL '{url}': {e}")
        return None, None
def user_agent():
    # Example of generating a random user-agent string
    user_agents = [
        # Windows (Intel)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4891.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4893.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4895.0 Safari/537.36",
        # Windows (ARM)
        "Mozilla/5.0 (Windows NT 10.0; Win64; arm64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4891.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; arm64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4893.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; arm64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4895.0 Safari/537.36",
        # Linux (x86_64)
        "Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4891.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4893.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4895.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        # macOS (Intel)
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
        # macOS (ARM)
        "Mozilla/5.0 (Macintosh; ARM Mac OS X 12_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; ARM Mac OS X 12_0_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
        # iOS Devices
        "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        # Android Devices
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4891.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4893.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4895.0 Mobile Safari/537.36",
        # Smart TVs
        "Mozilla/5.0 (SMART-TV; LINUX; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SmartTV/1.0",
        "Mozilla/5.0 (SMART-TV; LINUX; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) WebAppManager/1.0",
        # Game Consoles
        "Mozilla/5.0 (PlayStation 5 3.01) AppleWebKit/605.1.15 (KHTML, like Gecko)",
        "Mozilla/5.0 (Xbox One 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edge/44.18363.8740",
    ]
    agents = random.choice(user_agents)
    return agents

# # Function to change Tor IP address
# def renew_tor_ip():
#     with Controller.from_port(port=9051) as controller:
#         controller.authenticate()
#         controller.signal(Signal.NEWNYM)

# # Function to make requests through Tor
# def make_tor_request(url, max_retries=3):
#     renew_tor_ip()
#     headers = {"User-Agent": user_agent()}
#     session = requests.Session()
#     session.proxies = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}

#     for i in range(max_retries):
#         try:
#             response = session.get(url, headers=headers, timeout=10)
#             if response.status_code == 200:
#                 return response.text
#         except requests.exceptions.RequestException as e:
#             print(f"Error: {e}")
#         time.sleep(2)  # Add a delay between retries

#     return None


def find_links(url):
    links_href = []  # Initialize list to store extracted links
    content_type, content = fetch_all(url)
    base_url = urlparse(url)
    links = content.find_all("a", href=True)
    for link in links:
        link_href = link["href"]
        if not link_href.startswith(('http://', 'https://')):
            # Convert relative links to absolute links
            link_href = urljoin(base_url.geturl(), link_href)
        links_href.append(link_href)
    return links_href

def find_domain(links):
    domains = [urlparse(link).netloc for link in links]
    domain_counts = Counter(domains)
    most_common_domain = domain_counts.most_common(1)[0][0]
    # print(f"Most_frequent_domain:{most_common_domain}")
    return most_common_domain

# To determine which links are related to target domains(e.g., pages) you are interested in
def filter_links(links, domain=None, kind='html'):
    filtered_links = []
    if isinstance(kind, (str, list)):
        kind = tuple(kind)
    if domain is None:
        domain = find_domain(links)
    for link in links:
        parsed_link = urlparse(link)
        if parsed_link.netloc == domain and parsed_link.path.endswith(kind) and 'javascript:' not in parsed_link:
            filtered_links.append(link)
    return filtered_links

def find_img(url, dir_save="images"):
    """
    Save images referenced in HTML content locally.
    Args:
        content (str or BeautifulSoup): HTML content or BeautifulSoup object.
        url (str): URL of the webpage.
        content_type (str): Type of content. Default is "html".
        dir_save (str): Directory to save images. Default is "images".
    Returns:
        str: HTML content with updated image URLs pointing to local files.
    """
    content_type, content = fetch_all(url)
    if "html" in content_type.lower():
        # Create the directory if it doesn't exist
        os.makedirs(dir_save, exist_ok=True)

        # Parse HTML content if it's not already a BeautifulSoup object
        if isinstance(content, str):
            content = BeautifulSoup(content, "html.parser")
        image_links=[]
        # Extracting images
        images = content.find_all("img", src=True)
        for i, image in enumerate(images):
            try:
                # Get the image URL
                image_url = image["src"]

                if image_url.startswith("data:image"):
                    # Extract the image data from the data URI
                    mime_type, base64_data = image_url.split(",", 1)
                    # Determine the file extension from the MIME type
                    if ":" in mime_type:
                        # image_extension = mime_type.split(":")[1].split(";")[0]
                        image_extension = mime_type.split(":")[1].split(";")[0].split("/")[-1]
                    else:
                        image_extension = "png"  # Default to PNG if extension is not specified
                    # if 'svg+xml' in image_extension:
                    #     image_extension='svg'
                    image_data = base64.b64decode(base64_data)
                    # Save the image data to a file
                    image_filename = os.path.join(
                        dir_save, f"image_{i}.{image_extension}"
                    )
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_data)

                    # Update the src attribute of the image tag to point to the local file
                    image["src"] = image_filename
                else:
                    # Construct the absolute image URL
                    absolute_image_url = urljoin(url, image_url)

                    # Parse the image URL to extract the file extension
                    parsed_url = urlparse(absolute_image_url)
                    image_extension = os.path.splitext(parsed_url.path)[1]

                    # Download the image
                    image_response = requests.get(absolute_image_url)

                    # Save the image to a file
                    image_filename = os.path.join(
                        dir_save, f"image_{i}{image_extension}"
                    )
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_response.content)

                    # Update the src attribute of the image tag to point to the local file
                    image["src"] = image_filename
            except (requests.RequestException, KeyError) as e:
                print(f"Failed to process image {image_url}: {e}")
        print(f"images were saved at\n{dir_save}")
    # Return the HTML content with updated image URLs
    return content

def content_div_class(content, div="div", div_class="highlight"):
    texts = [div.text for div in content.find_all(div, class_=div_class)]
    return texts
def find(url, where="div", what="highlight"):
    _,content = fetch_all(url, parser="html.parser")
    texts = [div.text for div in content.find_all(where, class_=what)]
    return texts
# usage example:
#### img2local(url, "/Users/macjianfeng/Desktop/@tmp/dd/")
def find_forms(url):
    content_type, content = fetch_all(url)
    df=pd.DataFrame()
    # Extracting forms and inputs
    forms = content.find_all("form")
    form_data = []
    for form in forms:
        form_inputs = form.find_all("input")
        input_data = {}
        for input_tag in form_inputs:
            input_type = input_tag.get("type")
            input_name = input_tag.get("name")
            input_value = input_tag.get("value")
            input_data[input_name] = {"type": input_type, "value": input_value}
        form_data.append(input_data)
    return form_data
#  to clean strings
def clean_string(value):
    if isinstance(value, str):
        return value.replace('\n', '').replace('\r', '').replace('\t', '')
    else:
        return value
def find_all(url, dir_save=None):
    content_type, content = fetch_all(url)

    # Extracting paragraphs
    paragraphs_text = [paragraph.text for paragraph in content.find_all("p")]

    # Extracting specific elements by class
    specific_elements_text = [element.text for element in content.find_all(class_="specific-class")]

    # Extracting links (anchor tags)
    links_href = find_links(url)
    links_href = filter_links(links_href)

    # Extracting images
    images_src = [image['src'] for image in content.find_all("img", src=True)]

    # Extracting headings (h1, h2, h3, etc.)
    headings = [f'h{i}' for i in range(1, 7)]
    headings_text = {heading: [tag.text for tag in content.find_all(heading)] for heading in headings}

    # Extracting lists (ul, ol, li)
    list_items_text = [item.text for list_ in content.find_all(["ul", "ol"]) for item in list_.find_all("li")]

    # Extracting tables (table, tr, td)
    table_cells_text = [cell.text for table in content.find_all("table") for row in table.find_all("tr") for cell in row.find_all("td")]

    # Extracting other elements
    divs_content = [div.text.strip() for div in content.find_all("div")]
    headers_footer_content = [tag.text for tag in content.find_all(["header", "footer"])]
    meta_tags_content = [(tag.name, tag.attrs) for tag in content.find_all("meta")]
    spans_content = [span.text for span in content.find_all("span")]
    bold_text_content = [text.text for text in content.find_all("b")]
    italic_text_content = [text.text for text in content.find_all("i")]
    code_snippets_content = [code.text for code in content.find_all("code")]
    blockquotes_content = [blockquote.text for blockquote in content.find_all("blockquote")]
    preformatted_text_content = [pre.text for pre in content.find_all("pre")]
    buttons_content = [button.text for button in content.find_all("button")]
    navs_content = [nav.text for nav in content.find_all("nav")]
    sections_content = [section.text for section in content.find_all("section")]
    articles_content = [article.text for article in content.find_all("article")]
    figures_content = [figure.text for figure in content.find_all("figure")]
    captions_content = [caption.text for caption in content.find_all("figcaption")]
    abbreviations_content = [abbr.text for abbr in content.find_all("abbr")]
    definitions_content = [definition.text for definition in content.find_all("dfn")]
    addresses_content = [address.text for address in content.find_all("address")]
    time_elements_content = [time.text for time in content.find_all("time")]
    progress_content = [progress.text for progress in content.find_all("progress")]
    meter_content = [meter.text for meter in content.find_all("meter")]
    forms = find_forms(url)

    lists_to_fill = [
        paragraphs_text, specific_elements_text, links_href, images_src,
        headings_text["h1"], headings_text["h2"], headings_text["h3"], headings_text["h4"],
        headings_text["h5"], headings_text["h6"], list_items_text, table_cells_text,
        divs_content, headers_footer_content, meta_tags_content, spans_content,
        bold_text_content, italic_text_content, code_snippets_content,
        blockquotes_content, preformatted_text_content, buttons_content,
        navs_content, sections_content, articles_content, figures_content,
        captions_content, abbreviations_content, definitions_content,
        addresses_content, time_elements_content, progress_content,
        meter_content,forms
    ]
    # add new features
    script_texts=content_div_class(content, div="div", div_class="highlight")
    lists_to_fill.append(script_texts)
    
    audio_src = [audio['src'] for audio in content.find_all("audio", src=True)]
    video_src = [video['src'] for video in content.find_all("video", src=True)]
    iframe_src = [iframe['src'] for iframe in content.find_all("iframe", src=True)]
    lists_to_fill.extend([audio_src, video_src, iframe_src])
    
    rss_links = [link['href'] for link in content.find_all('link', type=['application/rss+xml', 'application/atom+xml'])]
    lists_to_fill.append(rss_links)

    # Find the maximum length among all lists
    max_length = max(len(lst) for lst in lists_to_fill)

    # Fill missing data with empty strings for each list
    for lst in lists_to_fill:
        lst += [""] * (max_length - len(lst))

    # Create DataFrame
    df = pd.DataFrame({
        "headings1": headings_text["h1"],
        "headings2": headings_text["h2"],
        "headings3": headings_text["h3"],
        "headings4": headings_text["h4"],
        "headings5": headings_text["h5"],
        "headings6": headings_text["h6"],
        "paragraphs": paragraphs_text,
        "list_items": list_items_text,
        "table_cells": table_cells_text,
        "headers_footer": headers_footer_content,
        "meta_tags": meta_tags_content,
        "spans": spans_content,
        "bold_text": bold_text_content,
        "italic_text": italic_text_content,
        "code_snippets": code_snippets_content,
        "blockquotes": blockquotes_content,
        "preformatted_text": preformatted_text_content,
        "buttons": buttons_content,
        "navs": navs_content,
        "sections": sections_content,
        "articles": articles_content,
        "figures": figures_content,
        "captions": captions_content,
        "abbreviations": abbreviations_content,
        "definitions": definitions_content,
        "addresses": addresses_content,
        "time_elements": time_elements_content,
        "progress": progress_content,
        "specific_elements": specific_elements_text,
        "meter": meter_content,
        "forms":forms,
        "scripts":script_texts,
        "audio":audio_src,
        "video":video_src,
        "iframe":iframe_src,
        "rss": rss_links,
        "images": images_src,
        "links": links_href,
        "divs": divs_content,
    })
    # to remove the '\n\t\r'
    df=df.apply(lambda x: x.map(clean_string) if x.dtype == "object" else x) # df=df.applymap(clean_string)
    if dir_save:
        if not dir_save.endswith(".csv"):
            dir_save=dir_save+"_df.csv"
            df.to_csv(dir_save)
        else:
            df.to_csv(dir_save)
        print(f"file has been saved at\n{dir_save}")
    return df
