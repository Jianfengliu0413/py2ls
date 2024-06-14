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
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Suppress WDM INFO logs
logging.getLogger('WDM').setLevel(logging.WARNING)
proxies_glob=None

# Define supported content types and corresponding parsers
CONTENT_PARSERS = {
    "text/html": lambda text, parser: BeautifulSoup(text, parser),
    "application/json": lambda text, parser: json.loads(text),
    "text/xml": lambda text, parser: BeautifulSoup(text, parser),
    "text/plain": lambda text, parser: text.text,
}

def user_agent(browsers=["chrome", "edge", "firefox", "safari"], platforms=["pc", "tablet"],verbose=False,os=["windows", "macos", "linux"]):
    ua = UserAgent(browsers=browsers, platforms=platforms,os=os)
    output_ua = ua.random
    if verbose:
        print(output_ua)
    return output_ua
# def extract_text_from_content(content,where,what,extend=False):
#     if extend:
#         texts = ""

#         def extract_text(element):
#             nonlocal texts
#             if isinstance(element, str) and element.strip():
#                 texts += element.strip()
#             elif hasattr(element, "children"):
#                 for child in element.children:
#                     extract_text(child)

#         result_set = (
#             content.find_all(where, class_=what)
#             if what
#             else content.find_all(where)
#         )
#         for tag in result_set:
#             extract_text(tag)

#         text = [tx for tx in texts.split("\n") if tx]
#         return text
#     else:
#         result_set = (
#             content.find_all(where, class_=what)
#             if what
#             else content.find_all(where)
#         )
#         texts_ = " ".join(tag.get_text() + "\n" for tag in result_set)
#         texts = [tx.strip() for tx in texts_.split("\n") if tx]
#         return texts
# def extract_text_from_content(content, where, what=None, extend=True):
#     if extend:
#         def extract_text(element):
#             texts = ""
#             if isinstance(element, str) and element.strip():
#                 texts += element.strip()
#             elif hasattr(element, "children"):
#                 for child in element.children:
#                     texts += extract_text(child)
#             return texts

#         result_set = content.find_all(where, class_=what) if what else content.find_all(where)
#         texts = ""
#         for tag in result_set:
#             texts += extract_text(tag) + "\n"
#         text_list = [tx.strip() for tx in texts.split("\n") if tx.strip()]
#         return text_list
#     else:
#         result_set = content.find_all(where, class_=what) if what else content.find_all(where)
#         texts_ = " ".join(tag.get_text() for tag in result_set)
#         texts = [tx.strip() for tx in texts_.split("\n") if tx.strip()]
#         return texts
def extract_text_from_content(content, content_type="text/html", where=None, what=None, extend=True, **kwargs):
    if content is None:
        logger.error("Content is None, cannot extract text.")
        return []

    if content_type not in CONTENT_PARSERS:
        logger.error(f"Unsupported content type: {content_type}")
        return []

    if "json" in content_type:
        where = None
        return extract_text_from_json(content, where)
    elif 'text' in content_type:
        if extend:
            def extract_text(element):
                texts = ""
                if isinstance(element, str) and element.strip():
                    texts += element.strip()
                elif hasattr(element, "children"):
                    for child in element.children:
                        texts += extract_text(child)
                return texts

            search_kwargs = {**kwargs}
            if what:
                search_kwargs["class_"] = what

            result_set = content.find_all(where, **search_kwargs)
            texts = ""
            for tag in result_set:
                texts += extract_text(tag) + "\n"
            text_list = [tx.strip() for tx in texts.split("\n") if tx.strip()]
            return text_list
        else:
            search_kwargs = {**kwargs}
            if what:
                search_kwargs["class_"] = what

            result_set = content.find_all(where, **search_kwargs)
            texts_ = " ".join(tag.get_text() for tag in result_set)
            texts = [tx.strip() for tx in texts_.split("\n") if tx.strip()]
            return texts

def extract_text_from_json(content, key=None):
    if key:
        if isinstance(content, list):
            return [str(item.get(key, '')) for item in content if key in item]
        if isinstance(content, dict):
            return [str(content.get(key, ''))]
    else:
        return [str(value) for key, value in flatten_json(content).items()]

def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def get_proxy():
    list_ = []
    headers = {"User-Agent": user_agent()}
    response = requests.get("https://free-proxy-list.net", headers=headers)
    content = BeautifulSoup(response.content, "html.parser")
    info = extract_text_from_content(content, where="td", extend=0)[0].split()
    count, pair_proxy = 0, 2
    for i, j in enumerate(info):
        if "." in j:
            list_.append(j + ":" + info[i + 1])
            # list_.append()  # Assuming the next item is the value
            count += 1
            # if count == pair_proxy:  # Stop after extracting the desired number of pairs
            #     break
    prox = random.sample(list_, 2)
    proxies = {
        "http": f"http://" + prox[0],
        "https": f"http://" + prox[1],
    }
    return proxies
# proxies_glob=get_proxy()

def fetch_all(url, parser="lxml"):  # lxml is faster, # parser="html.parser"
    try:
        # Generate a random user-agent string
        headers = {"User-Agent": user_agent()}

        # Send the initial request
        response = requests.get(url, headers=headers,proxies=proxies_glob)

        # If the response is a redirect, follow it
        while response.is_redirect:
            logger.info(f"Redirecting to: {response.headers['Location']}")
            response = requests.get(response.headers["Location"], headers=headers,proxies=proxies_glob)
        # Check for a 403 error
        if response.status_code == 403:
            logger.warning("403 Forbidden error. Retrying...")
            # Retry the request after a short delay
            sleep(random.uniform(1, 3))
            response = requests.get(url, headers=headers,proxies=proxies_glob)
            # Raise an error if retry also fails
            response.raise_for_status()

        # Raise an error for other HTTP status codes
        response.raise_for_status()

        # Get the content type
        content_type = response.headers.get("content-type", "").split(";")[0].lower()
        if response.encoding:
            content = response.content.decode(response.encoding)
        else:
            content=None
        # logger.info(f"Content type: {content_type}")

        # Check if content type is supported
        if content_type in CONTENT_PARSERS and content:
            return content_type, CONTENT_PARSERS[content_type](content, parser)
        else:
            logger.warning("Unsupported content type")
            return None, None
    except requests.RequestException as e:
        logger.error(f"Error fetching URL '{url}': {e}")
        return None, None



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
    links_href,cond_ex= [],["javascript:","mailto:","tel:","fax:"]
    content_type, soup = fetch_all(url)
    if soup:
        base_url = urlparse(url)
        links = soup.find_all("a", href=True, recursive=True)
        for link in links:
            link_href = link["href"]
            if not link_href.startswith(("http")):
                link_href = urljoin(base_url.geturl(), link_href)
            cond_ex_ = all([i not in link_href for i in cond_ex])
            if cond_ex_:
                links_href.append(link_href)
        return list(set(links_href)) 
    elif url.split('.')[-1] in ['pdf']:
        return url
    else:
        return None


def find_domain(links):
    if not links:
        return None
    domains = [urlparse(link).netloc for link in links]
    domain_counts = Counter(domains)
    if domain_counts.most_common(1):
        most_common_domain_tuple = domain_counts.most_common(1)[0]
        if most_common_domain_tuple:
            most_common_domain = most_common_domain_tuple[0]
            return most_common_domain
        else:
            return None
    else:
        return None


# To determine which links are related to target domains(e.g., pages) you are interested in
def filter_links(links, contains="html"):
    filtered_links = []
    if isinstance(contains, str):
        contains = [contains]
    if isinstance(links,str):
        links=find_links(links)
    for link in links:
        parsed_link = urlparse(link) 
        condition = (all([i in link for i in contains])
            and "javascript:" not in parsed_link
        ) 
        if condition:
            filtered_links.append(link)
    return filtered_links


def pdf_detector(url, contains=None, dir_save=None,booster=False):
    def fname_pdf_corr(fname):
        if fname[-4:]!='.pdf':
            fname = fname[:-4] + '.pdf'
        return fname
    if isinstance(contains, str):
        contains = [contains]
    if isinstance(url,str):
        if '.pdf' in url:
            pdf_links=url
        else:
            if booster:
                links_all=[]
                if 'http' in url and url:
                    [links_all.append(i) for i in find_links(url) if 'http' in i]
                print(links_all)
            else:
                links_all=url
            if contains is not None:
                pdf_links = filter_links(links=links_all, contains=[".pdf"] + contains)
            else:
                pdf_links = filter_links(links=links_all, contains=[".pdf"])
    elif isinstance(url,list):
        links_all=url        
        if contains is not None:
            pdf_links = filter_links(links=links_all, contains=["pdf"] + contains)
        else:
            pdf_links = filter_links(links=links_all, contains=["pdf"])
    else:
        links_all = find_links(url)
        if contains is not None:
            pdf_links = filter_links(links=links_all, contains=["pdf"] + contains)
        else:
            pdf_links = filter_links(links=links_all, contains=["pdf"])

    if pdf_links:
        print(f"pdf detected\n{pdf_links}")
    else:
        print('no pdf file')
    if dir_save:
        print("... is trying to download to local")
        fnames = [pdf_link_.split("/")[-1] for pdf_link_ in pdf_links]
        idx = 0
        for pdf_link in pdf_links:
            headers = {"User-Agent": user_agent()}
            response = requests.get(pdf_link, headers=headers)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Save the PDF content to a file
                with open(dir_save + fname_pdf_corr(fnames[idx]), "wb") as pdf:
                    pdf.write(response.content)
                print("PDF downloaded successfully!")
            else:
                print("Failed to download PDF:", response.status_code)
            idx += 1
        print(f'{len(fnames)} files are downloaded:\n{fnames}\n to local: \n{dir_save}')


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
        image_links = []
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
                        image_extension = (
                            mime_type.split(":")[1].split(";")[0].split("/")[-1]
                        )
                    else:
                        image_extension = (
                            "png"  # Default to PNG if extension is not specified
                        )
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
                    image_response = requests.get(absolute_image_url,proxies=proxies_glob)

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



def fetch_selenium(
    url,
    where="div",
    what=None,
    extend=False,
    by=By.TAG_NAME,
    timeout=10,
    retry=2,
    login_url=None,
    username=None,
    password=None,
    username_field="username",
    password_field="password",
    submit_field="submit",
    username_by=By.NAME,
    password_by=By.NAME,
    submit_by=By.NAME,
    proxy=None,  # Add proxy parameter
    **kwargs
):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={user_agent()}")
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    service = Service(ChromeDriverManager().install()) 
    for attempt in range(retry):
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            if login_url:
                driver.get(login_url)
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((username_by, username_field))
                ).send_keys(username)
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((password_by, password_field))
                ).send_keys(password)
                WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((submit_by, submit_field))
                ).click()

            driver.get(url)
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, where))
            )
            page_source = driver.page_source
            driver.quit()

            content = BeautifulSoup(page_source, "html.parser")
            texts=extract_text_from_content(content, where=where,what=what,extend=extend,**kwargs)
            return texts
        except Exception as e:
            # logger.error(f"Attempt {attempt + 1} failed with error ")
            if driver:
                driver.quit()
            if attempt == retry - 1:
                logger.error("Failed to fetch the content after all retries")
                return []
        sleep(random.uniform(1, 3))
    # Return empty list if nothing found after all retries
    return []


def fetch(url, where="div", what=None, extend=True, booster=False,retry=2,verbose=False, **kws):
    # for attempt in range(retry):
    #     if verbose and attempt==0:
    #         xample = 'fetch(url,where="div",what=None,extend=True,by=By.TAG_NAME,timeout=10,retry=3,login_url=None,username=None,password=None,username_field="username",password_field="password",submit_field="submit",username_by=By.NAME,password_by=By.NAME,submit_by=By.NAME)'
    #         print(xample)
    #     content_type, content = fetch_all(url, parser="html.parser")
    #     texts=extract_text_from_content(content,content_type=content_type,where=where,what=what,extend=extend, **kws)
    #     if isinstance(texts,pd.core.frame.DataFrame):
    #         condition=[texts.empty, attempt != retry - 1]
    #     else:
    #         condition=[not texts, attempt != retry - 1]
    #     if all(condition):
    #         texts = fetch(url=url, where=where, what=what, extend=extend, retry=retry-1, **kws)
    #     sleep(random.uniform(0.5, 1.5))
    for attempt in range(retry):
        if verbose and attempt==0:
            xample = 'fetch(url,where="div",what=None,extend=True,by=By.TAG_NAME,timeout=10,retry=3,login_url=None,username=None,password=None,username_field="username",password_field="password",submit_field="submit",username_by=By.NAME,password_by=By.NAME,submit_by=By.NAME)'
            print(xample)
        content_type, content = fetch_all(url, parser="html.parser")
        texts=extract_text_from_content(content,content_type=content_type,where=where,what=what,extend=extend, **kws)
        if isinstance(texts, pd.core.frame.DataFrame):
            # condition=[texts.empty, attempt != retry - 1]
            if not texts.empty:
                break
        else:
            # condition=[not texts, attempt != retry - 1]
            if texts:
                break
        # if all(condition):
        #     texts = fetch(url=url, where=where, what=what, extend=extend, retry=retry-1, **kws)
        sleep(random.uniform(0.5, 1.5))
    if isinstance(texts,pd.core.frame.DataFrame):
        condition_=[texts.empty, booster]
    else:
        condition_=[not texts, booster]
    if any(condition_):
        print("trying to use 'fetcher2'...")
        texts = fetch_selenium(url=url, where=where, what=what, extend=extend, **kws)
    return texts


def extract_from_content(content, where="div", what=None):
    if what is None:
        result_set = content.find_all(where,recursive=True)
        texts_ = " ".join(tag.get_text() + "\n" for tag in result_set)
        texts = [tx for tx in texts_.split("\n") if tx]
    else:
        texts_ = " ".join(
            div.get_text() + "\n" for div in content.find_all(where, class_=what,recursive=True)
        )
        texts = [tx for tx in texts_.split("\n") if tx]
    return texts


def find_forms(url):
    content_type, content = fetch_all(url)
    df = pd.DataFrame()
    # Extracting forms and inputs
    forms = content.find_all("form",recursive=True)
    form_data = []
    for form in forms:
        if form:
            form_inputs = form.find_all("input",recursive=True)
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
        return value.replace("\n", "").replace("\r", "").replace("\t", "")
    else:
        return value


def find_all(url, dir_save=None):
    content_type, content = fetch_all(url)
    paragraphs_text = extract_from_content(content, where="p")
    # Extracting specific elements by class
    specific_elements_text = [
        element.text for element in content.find_all(class_="specific-class",recursive=True) if element
    ]
    # Extracting links (anchor tags)
    links_href = find_links(url)
    links_href = filter_links(links_href)

    # Extracting images
    images_src = [image["src"] for image in content.find_all("img", src=True,recursive=True) if image]

    # Extracting headings (h1, h2, h3, etc.)
    headings = [f"h{i}" for i in range(1, 7)]
    headings_text = {
        heading: [tag.text for tag in content.find_all(heading,recursive=True)]
        for heading in headings
        if heading
    }

    # Extracting lists (ul, ol, li)
    list_items_text = [
        item.text
        for list_ in content.find_all(["ul", "ol"],recursive=True)
        for item in list_.find_all("li",recursive=True)
        if item
    ]

    # Extracting tables (table, tr, td)
    table_cells_text = [
        cell.text
        for table in content.find_all("table",recursive=True)
        for row in table.find_all("tr")
        for cell in row.find_all("td")
        if cell
    ]

    # Extracting other elements
    divs_content = extract_from_content(content, where="div")
    headers_footer_content = [
        tag.text for tag in content.find_all(["header", "footer"],recursive=True) if tag
    ]
    meta_tags_content = [
        (tag.name, tag.attrs) for tag in content.find_all("meta",recursive=True) if tag
    ]
    spans_content = extract_from_content(content, where="span")
    bold_text_content = extract_from_content(content, where="b")
    italic_text_content = extract_from_content(content, where="i")
    code_snippets_content = extract_from_content(content, where="code")
    blockquotes_content = extract_from_content(content, where="blockquote")
    preformatted_text_content = extract_from_content(content, where="pre")
    buttons_content = extract_from_content(content, where="button")
    navs_content = extract_from_content(content, where="nav")
    sections_content = extract_from_content(content, where="section")
    articles_content = extract_from_content(content, where="article")
    figures_content = extract_from_content(content, where="figure")
    captions_content = extract_from_content(content, where="figcap")
    abbreviations_content = extract_from_content(content, where="abbr")
    definitions_content = extract_from_content(content, where="dfn")
    addresses_content = extract_from_content(content, where="address")
    time_elements_content = extract_from_content(content, where="time")
    progress_content = extract_from_content(content, where="process")
    forms = find_forms(url)

    lists_to_fill = [
        paragraphs_text,
        specific_elements_text,
        links_href,
        images_src,
        headings_text["h1"],
        headings_text["h2"],
        headings_text["h3"],
        headings_text["h4"],
        headings_text["h5"],
        headings_text["h6"],
        list_items_text,
        table_cells_text,
        divs_content,
        headers_footer_content,
        meta_tags_content,
        spans_content,
        bold_text_content,
        italic_text_content,
        code_snippets_content,
        blockquotes_content,
        preformatted_text_content,
        buttons_content,
        navs_content,
        sections_content,
        articles_content,
        figures_content,
        captions_content,
        abbreviations_content,
        definitions_content,
        addresses_content,
        time_elements_content,
        progress_content,
        forms,
    ]
    # add new features
    script_texts = content_div_class(content, div="div", div_class="highlight")
    lists_to_fill.append(script_texts)

    audio_src = [audio["src"] for audio in content.find_all("audio", src=True,recursive=True)]
    video_src = [video["src"] for video in content.find_all("video", src=True,recursive=True)]
    iframe_src = [iframe["src"] for iframe in content.find_all("iframe", src=True,recursive=True)]
    lists_to_fill.extend([audio_src, video_src, iframe_src])

    rss_links = [
        link["href"]
        for link in content.find_all(
            "link", type=["application/rss+xml", "application/atom+xml"],recursive=True
        )
    ]
    lists_to_fill.append(rss_links)

    # Find the maximum length among all lists
    max_length = max(len(lst) for lst in lists_to_fill)

    # Fill missing data with empty strings for each list
    for lst in lists_to_fill:
        lst += [""] * (max_length - len(lst))

    # Create DataFrame
    df = pd.DataFrame(
        {
            "h1": headings_text["h1"],
            "h2": headings_text["h2"],
            "h3": headings_text["h3"],
            "h4": headings_text["h4"],
            "h5": headings_text["h5"],
            "h6": headings_text["h6"],
            "paragraphs": paragraphs_text,
            "divs": divs_content,
            "items": list_items_text,
            "tables": table_cells_text,
            "headers": headers_footer_content,
            "tags": meta_tags_content,
            "spans": spans_content,
            "bold_text": bold_text_content,
            "italic_text": italic_text_content,
            "codes": code_snippets_content,
            "blocks": blockquotes_content,
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
            "forms": forms,
            "scripts": script_texts,
            "audio": audio_src,
            "video": video_src,
            "iframe": iframe_src,
            "rss": rss_links,
            "images": images_src,
            "links": links_href,
        }
    )
    # to remove the '\n\t\r'
    df = df.apply(
        lambda x: x.map(clean_string) if x.dtype == "object" else x
    )  # df=df.applymap(clean_string)
    if dir_save:
        if not dir_save.endswith(".csv"):
            dir_save = dir_save + "_df.csv"
            df.to_csv(dir_save)
        else:
            df.to_csv(dir_save)
        print(f"file has been saved at\n{dir_save}")
    return df