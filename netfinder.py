from bs4 import BeautifulSoup
import requests
from requests.utils import dict_from_cookiejar
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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pprint import pp
import mimetypes
import io
import matplotlib.pyplot as plt
from PIL import Image
from duckduckgo_search import DDGS
from datetime import datetime
import time
from py2ls import ips

dir_save='/Users/macjianfeng/Dropbox/Downloads/'
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
def extract_text_from_content(content, content_type="text/html", where=None, what=None, extend=True, **kwargs):
    """
    Extracts text from the given content based on the specified content type and search criteria.

    Parameters:
    - content (str/BeautifulSoup): The content to extract text from.
    - content_type (str): The type of content, e.g., "text/html" or "application/json".
    - where (str/list): The HTML tag or list of tags to search for.
    - what (str): The class name to filter the tags (optional).
    - extend (bool): Whether to recursively extract text from child elements.
    - **kwargs: Additional keyword arguments for the search (e.g., id, attributes).

    Returns:
    - list: A list of extracted text segments.
    """
    def extract_text(element):
        texts = ""
        if isinstance(element, str) and element.strip():
            texts += element.strip()
        elif hasattr(element, "children"):
            for child in element.children:
                texts += extract_text(child)
        return texts
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
        if isinstance(where, list):
            res=[]
            for where_ in where:
                res.extend(extract_text_from_content(content, content_type="text/html", where=where_, what=what, extend=extend, **kwargs))
            return res
        else:
            search_kwargs = {**kwargs}
            # correct 'class_'
            # dict_=dict(class_="gsc_mnd_art_info")
            if 'class_' in search_kwargs:
                search_kwargs["class"]=search_kwargs["class_"]
                del search_kwargs['class_']
            if what:
                search_kwargs["class"] = what
            if 'attrs' in kwargs:
                result_set = content.find_all(where, **search_kwargs)
                print(f"attrs =>{search_kwargs}")
            else:
                result_set = content.find_all(where, attrs=dict(**search_kwargs))
                print(f"{search_kwargs}")
            
            if not result_set:
                print("Failed: check the 'attrs' setting:  attrs={'id':'xample'}")
            if extend:
                texts = ""
                for tag in result_set:
                    texts += extract_text(tag) + "\n"
                text_list = [tx.strip() for tx in texts.split("\n") if tx.strip()]
                return text_list
            else:
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
def get_soup(url, driver='req'):
    _,soup_=fetch_all(url, driver=driver)
    return soup_
def fetch_all(url, parser="lxml", driver='request', # request or selenium
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
    # capability='eager', # eager or none
    proxy=None,  # Add proxy parameter
    javascript=True,  # Add JavaScript option
    disable_images=False,  # Add option to disable images
    iframe_name=None):  # Add option to handle iframe):  # lxml is faster, # parser="html.parser"
    try:
        # # Generate a random user-agent string
        # response = requests.get(url)
        # # get cookies
        # cookie=dict_from_cookiejar(response.cookies)
        # # get token from cookies
        # scrf_token=re.findall(r'csrf-token=(.*?);', response.headers.get('Set-Cookie'))[0]
        # headers = {"User-Agent": user_agent(), "X-CSRF-Token":scrf_token}
        
        headers = {"User-Agent": user_agent()}
        if 'req' in driver.lower():
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
        elif 'se' in driver.lower():
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={user_agent()}")
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')
            if disable_images:
                prefs = {"profile.managed_default_content_settings.images": 2}
                chrome_options.add_experimental_option("prefs", prefs)
            # chrome_options.page_load_strategy = capability
            service = Service(ChromeDriverManager().install())

            driver_ = webdriver.Chrome(service=service, options=chrome_options)
            
            if not javascript:
                driver_.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})

            if login_url:
                driver_.get(login_url)
                WebDriverWait(driver_, timeout).until(
                    EC.presence_of_element_located((username_by, username_field))
                ).send_keys(username)
                WebDriverWait(driver_, timeout).until(
                    EC.presence_of_element_located((password_by, password_field))
                ).send_keys(password)
                WebDriverWait(driver_, timeout).until(
                    EC.element_to_be_clickable((submit_by, submit_field))
                ).click()

            driver_.get(url)
            
            if iframe_name:
                iframe = WebDriverWait(driver_, timeout).until(
                    EC.presence_of_element_located((By.NAME, iframe_name))
                )
                driver_.switch_to.frame(iframe)

            # WebDriverWait(driver, timeout).until(
            #     EC.presence_of_element_located((by, where))
            # )
            page_source = driver_.page_source
            driver_.quit()

            content = BeautifulSoup(page_source, "html.parser")
            if content: 
                return 'text/html', content
            else:
                logger.warning("Selenium could not fetch content")
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


# def find_links(url,driver='request'):
#     links_href,cond_ex= [],["javascript:","mailto:","tel:","fax:"]
#     content_type, soup = fetch_all(url,driver=driver)
#     if soup:
#         base_url = urlparse(url)
        
#         # Extract links from both 'href' and 'src' attributes across relevant tags
#         tags_with_links = ['a', 'img', 'script', 'link', 'iframe', 'embed','span']
#         elements = []
#         for tag in tags_with_links:
#             elements.extend(soup.find_all(tag, href=True))
#             elements.extend(soup.find_all(tag, src=True))
        
#         for element in elements:
#             link_href = element.get('href') or element.get('src')
#             if link_href:
#                 if link_href.startswith("//"):
#                     link_href = "http:" + link_href
#                 elif not link_href.startswith(("http", "https")):
#                     link_href = urljoin(base_url.geturl(), link_href)
                
#                 if all(exclusion not in link_href for exclusion in cond_ex):
#                     links_href.append(link_href)
        
#         return list(set(links_href))  # Remove duplicates

#     elif url.split('.')[-1] in ['pdf']:
#         return url
#     else:
#         return None
def find_links(url, driver='request', booster=False):
    links_href, cond_ex = [], ["javascript:", "mailto:", "tel:", "fax:"]
    content_type, soup = fetch_all(url, driver=driver)
    
    if soup and content_type=='text/html':
        base_url = urlparse(url)
        
        # Extract links from all tags with 'href' and 'src' attributes
        elements = soup.find_all(True, href=True) + soup.find_all(True, src=True)
        
        for element in elements:
            link_href = element.get('href') or element.get('src')
            if link_href:
                if link_href.startswith("//"):
                    link_href = "http:" + link_href
                elif not link_href.startswith(("http", "https")):
                    link_href = urljoin(base_url.geturl(), link_href)
                
                if all(exclusion not in link_href for exclusion in cond_ex):
                    links_href.append(link_href)
        
        unique_links = list(set(links_href))  # Remove duplicates
        
        if booster:
            for link in unique_links:
                if link != url:  # Avoid infinite recursion
                    sub_links = find_links(link, driver=driver, booster=False)
                    if sub_links:
                        links_href.extend(sub_links)
            links_href = list(set(links_href))  # Remove duplicates again
        
        return links_href

    elif url.split('.')[-1] in ['pdf']:
        return [url]
    else:
        return None
 

# To determine which links are related to target domains(e.g., pages) you are interested in
def filter_links(links, contains="html",driver='requ', booster=False):
    filtered_links = []
    if isinstance(contains, str):
        contains = [contains]
    if isinstance(links,str):
        links=find_links(links,driver=driver,booster=booster)
    for link in links:
        parsed_link = urlparse(link) 
        condition = (all([i in link for i in contains])
            and "javascript:" not in parsed_link
        ) 
        if condition:
            filtered_links.append(link)
    return filtered_links


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


def pdf_detector(url, contains = None, dir_save = None, booster = False):
    print("usage: pdf_detector(url, dir_save, booster=True")
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
        pp(f"pdf detected{pdf_links}")
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

def downloader(url, dir_save=dir_save, kind=['.pdf'], contains=None, rm_folder=False, booster=False,verbose=True):
    if verbose:
        print("usage: downloader(url, dir_save=None, kind=['.pdf','xls'], contains=None, booster=False)")
    def fname_corrector(fname, ext):
        if not ext.startswith("."):
            ext="."+ext
        if not fname.endswith("ext"):#if not ext in fname:
            fname = fname[:-len(ext)] + ext
        return fname
    def check_and_modify_filename(directory, filename):
        base, ext = os.path.splitext(filename)
        counter = 2
        new_filename = filename
        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{base}_{counter}{ext}"
            counter += 1
        return new_filename
    if not isinstance(kind,list):
        kind=[kind]
    if isinstance(url, list):
        for url_ in url:
            downloader(url_, dir_save=dir_save, kind=kind, contains=contains, booster=booster,verbose=verbose)
            # sleep(random.uniform(1, 3))
    for i,k in enumerate(kind):
        if not k.startswith('.'):
            kind[i]='.'+kind[i] 
    file_links_all=[]
    for kind_ in kind:
        print(kind_)
        if isinstance(contains, str):
            contains = [contains]
        if isinstance(url, str):
            if any(ext in url for ext in kind):
                file_links = [url]
            else:
                if booster:
                    links_all = []
                    if 'http' in url:
                        links_all = find_links(url) 
                else:
                    links_all = url
                if contains is not None:
                    file_links = filter_links(links_all, contains=contains + kind_)
                else:
                    file_links = links_all#filter_links(links_all, contains=kind_)
        elif isinstance(url, list):
            links_all = url        
            if contains is not None:
                file_links = filter_links(links_all, contains=contains + kind_)
            else:
                file_links = filter_links(links_all, contains=kind_)
        else:
            links_all = find_links(url)
            if contains is not None:
                file_links = filter_links(links_all, contains=contains + kind_)
            else:
                file_links = filter_links(links_all, contains=kind_) 
        if verbose:
            if file_links:
                print("Files detected:")
                pp(file_links)
            else:
                file_links=[]
                print('No files detected')
        file_links_all.extend(file_links)
    if dir_save:
        if rm_folder:
            ips.rm_folder(dir_save)
        if verbose:
            print(f"\n... attempting to download to local\n")
        fnames = [file_link.split("/")[-1] for file_link in file_links_all]
        for idx, file_link in enumerate(file_links_all):
            headers = {"User-Agent": user_agent()}
            response = requests.get(file_link, headers=headers)
            if response.status_code == 200:
                ext = next((ftype for ftype in kind if ftype in file_link), None)
                if ext:
                    corrected_fname = fname_corrector(fnames[idx], ext)
                    corrected_fname = check_and_modify_filename(dir_save, corrected_fname)
                    with open(os.path.join(dir_save, corrected_fname), "wb") as file:
                        file.write(response.content)
                    if verbose:
                        print(f"Done! {fnames[idx]}")
                else:
                    if verbose:
                        print(f"Unknown file type for {file_link}")
            else:
                if verbose:
                    print(f"Failed to download file: {response.status_code}")
        print(f'\n{len(fnames)} files were downloaded:')
        if verbose:
            pp(fnames)
            print(f"\n\nsaved @:\n{dir_save}")
        
def find_img(url, driver='request',dir_save="images", rm_folder=False, verbose=True):
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
    if rm_folder:
        ips.rm_folder(dir_save)
    content_type, content = fetch_all(url,driver=driver)
    print(content_type)
    if "html" in content_type.lower():
        # Create the directory if it doesn't exist
        os.makedirs(dir_save, exist_ok=True)
        # Parse HTML content if it's not already a BeautifulSoup object
        if isinstance(content, str):
            content = BeautifulSoup(content, "html.parser")
        image_links = []
        # Extracting images
        images = content.find_all("img", src=True)
        if not images:
            content_type, content = fetch_all(url,driver='selenium')
            images = content.find_all("img", src=True)
        for i, image in enumerate(images):
            try:
                image_url = image["src"]
                if image_url.startswith("data:image"):
                    mime_type, base64_data = image_url.split(",", 1)
                    if ":" in mime_type:
                        # image_extension = mime_type.split(":")[1].split(";")[0]
                        image_extension = (
                            mime_type.split(":")[1].split(";")[0].split("/")[-1]
                        )
                    else:
                        image_extension = (
                            "png"  # Default to PNG if extension is not specified
                        )
                    image_data = base64.b64decode(base64_data)
                    image_filename = os.path.join(
                        dir_save, f"image_{i}.{image_extension}"
                    )
                    with open(image_filename, "wb") as image_file:
                        image_file.write(image_data)
                    image["src"] = image_filename
                    # if verbose:
                    #     plt.imshow(image_data)
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
        if verbose:
            display_thumbnail_figure(flist(dir_save,filter='img'),dpi=100)
    return content

def svg_to_png(svg_file):
    with WandImage(filename=svg_file, resolution=300) as img:
        img.format = 'png'
        png_image = img.make_blob()
    return Image.open(io.BytesIO(png_image))

def display_thumbnail_figure(dir_img_list,figsize=(10,10),dpi=100):
    import matplotlib.pyplot as plt
    from PIL import Image
    """
    Display a thumbnail figure of all images in the specified directory.
    Args:
        dir_img_list (list): List of the Directory containing the images.
    """
    num_images = len(dir_img_list)
    if num_images == 0:
        print("No images found to display.")
        return
    grid_size = int(num_images ** 0.5) + 1
    fig, axs = plt.subplots(grid_size, grid_size, figsize=figsize,dpi=dpi)
    for ax, image_file in zip(axs.flatten(), dir_img_list):
        try:
            img = Image.open(image_file)
            ax.imshow(img)
            ax.axis('off')  # Hide axes
        except:
            continue
    try:
        [ax.axis("off") for ax in axs.flatten()]
        plt.tight_layout()
        plt.show()
    except:
        pass

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
    # capability='eager', # eager or none
    proxy=None,  # Add proxy parameter
    javascript=True,  # Add JavaScript option
    disable_images=False,  # Add option to disable images
    iframe_name=None,  # Add option to handle iframe
    **kwargs
):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={user_agent()}")
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.page_load_strategy = capability
    service = Service(ChromeDriverManager().install())
    for attempt in range(retry):
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            if not javascript:
                driver.execute_cdp_cmd("Emulation.setScriptExecutionDisabled", {"value": True})

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
            
            if iframe_name:
                iframe = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.NAME, iframe_name))
                )
                driver.switch_to.frame(iframe)

            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, where))
            )
            page_source = driver.page_source
            driver.quit()

            content = BeautifulSoup(page_source, "html.parser")
            texts = extract_text_from_content(content, where=where, what=what, extend=extend, **kwargs)
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


def fetch(url, where="div", driver='request',what=None, extend=True, booster=False,retry=2,verbose=False, output="text", **kws):
    print(f"output is {output}")
    if 'xt' in output.lower():
        for attempt in range(retry):
            if verbose and attempt==0:
                xample = 'fetch(url,where="div",what=None,extend=True,by=By.TAG_NAME,timeout=10,retry=3,login_url=None,username=None,password=None,username_field="username",password_field="password",submit_field="submit",username_by=By.NAME,password_by=By.NAME,submit_by=By.NAME)'
                print(xample)
            content_type, content = fetch_all(url, parser="html.parser",driver=driver)
            texts=extract_text_from_content(content,content_type=content_type,where=where,what=what,extend=extend, **kws)
            if isinstance(texts, pd.core.frame.DataFrame): 
                if not texts.empty:
                    break
            else: 
                if texts:
                    break
                sleep(random.uniform(0.5, 1.5))
        if isinstance(texts,pd.core.frame.DataFrame):
            condition_=[texts.empty, booster]
        else:
            condition_=[not texts, booster]
        if any(condition_):
            print("trying to use 'fetcher2'...")
            texts = fetch_selenium(url=url, where=where, what=what, extend=extend, **kws)
        if texts:
            return texts
        else:
            return fetch(url, where=where, driver=driver,what=what, extend=extend, booster=booster,retry=retry,verbose=verbose, output="soup", **kws)
    elif "url" in output.lower():
        base_url = urlparse(url)
        if verbose:
            print("urljoin(urlparse(url), link_part)")
        return base_url.geturl()
    else:
        try:
            content_type, content = fetch_all(url, parser="html.parser",driver=driver)
            search_kwargs = {**kws}
            print(search_kwargs)
            if 'class_' in search_kwargs:
                search_kwargs["class"]=search_kwargs["class_"]
                del search_kwargs['class_']
            if what:
                search_kwargs["class"] = what
            if 'attrs' in kws:
                result_set = content.find_all(where, **search_kwargs)
                print(f"attrs =>{search_kwargs}")
            else:
                result_set = content.find_all(where, attrs=dict(**search_kwargs))
                print(f"{search_kwargs}")
            return result_set
        except:
            print("got nothing")
            return None


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


def find_forms(url, driver='requ'):
    content_type, content = fetch_all(url,driver=driver)
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


def find_all(url, dir_save=None, driver='req'):
    content_type, content = fetch_all(url,driver=driver)
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


def flist(fpath, filter="all"):
    all_files = [os.path.join(fpath, f) for f in os.listdir(fpath) if os.path.isfile(os.path.join(fpath, f))]
    if isinstance(filter, str):
        filter=[filter]
    if isinstance(filter, list):
        filt_files=[]
        for filter_ in filter:
            filt_files.extend(flist(fpath, filter_))
        return filt_files
    else:
        if 'all' in filter.lower():
            return all_files
        else:
            filt_files = [f for f in all_files if istype(f, filter)]
        return filt_files

def istype(fpath, filter='img'):
    """
    Filters file paths based on the specified filter.
    Args:
        fpath (str): Path to the file.
        filter (str): filter of file to filter. Default is 'img' for images. Other options include 'doc' for documents,
                    'zip' for ZIP archives, and 'other' for other types of files.
    Returns:
        bool: True if the file matches the filter, False otherwise.
    """
    if 'img' in filter.lower():
        return is_image(fpath)
    elif 'doc' in filter.lower():
        return is_document(fpath)
    elif 'zip' in filter.lower():
        return is_zip(fpath)
    else:
        return False

def is_image(fpath):
    mime_type, _ = mimetypes.guess_type(fpath)
    if mime_type and mime_type.startswith('image'):
        return True
    else:
        return False

def is_document(fpath):
    mime_type, _ = mimetypes.guess_type(fpath)
    if mime_type and (
        mime_type.startswith('text/') or
        mime_type == 'application/pdf' or
        mime_type == 'application/msword' or
        mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or
        mime_type == 'application/vnd.ms-excel' or
        mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or
        mime_type == 'application/vnd.ms-powerpoint' or
        mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ):
        return True
    else:
        return False

def is_zip(fpath):
    mime_type, _ = mimetypes.guess_type(fpath)
    if mime_type == 'application/zip':
        return True
    else:
        return False

def search(query, limit=5, kind='text', output='df',verbose=False,download=False, dir_save=dir_save):

    if 'te' in kind.lower():
        results = DDGS().text(query, max_results=limit)
        res=pd.DataFrame(results)
        res.rename(columns={"href":"links"},inplace=True)
    if verbose:
        print(f'searching "{query}": got the results below\n{res}')
    if download:
        try:
            downloader(url=res.links.tolist(), dir_save=dir_save, verbose=verbose)
        except:
            if verbose:
                print(f"failed link")
    return res

def echo(query, model="gpt", verbose=True, log=True, dir_save=dir_save):
    def is_in_any(str_candi_short, str_full, ignore_case=True):
        if isinstance(str_candi_short, str):
            str_candi_short=[str_candi_short]
        res_bool=[]
        if ignore_case:
            [res_bool.append(i in str_full.lower())  for i in str_candi_short ]
        else:
            [res_bool.append(i in str_full)  for i in str_candi_short ]
        return any(res_bool)
    def valid_mod_name(str_fly):
        if is_in_any(str_fly, "claude-3-haiku"):
            return "claude-3-haiku"
        elif is_in_any(str_fly, "gpt-3.5"):
            return "gpt-3.5"
        elif is_in_any(str_fly, "llama-3-70b"):
            return "llama-3-70b"
        elif is_in_any(str_fly, "mixtral-8x7b"):
            return "mixtral-8x7b"
        else:
            print(f"not support your model{model}, supported models: 'claude','gpt(default)', 'llama','mixtral'")
            return "gpt-3.5" # default model
    model_valid = valid_mod_name(model)
    res=DDGS().chat(query, model=model_valid)
    if verbose:
        pp(res)
    if log:
        dt_str=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
        res_ = f"###{dt_str}\n\n>{res}\n"
        os.makedirs(dir_save, exist_ok=True)
        fpath = os.path.join(dir_save, f"log_ai.md")
        ips.fupdate(fpath=fpath,content=res_)
        print(f"log file:{fpath}")
    return res

def chat(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], str):
        kwargs['query'] = args[0]
    return echo(**kwargs)

def ai(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], str):
        kwargs['query'] = args[0]
    return echo(**kwargs)