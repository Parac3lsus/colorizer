#This script will generate dataset from google images searching for key words in CLASSES_SEARCH
#and downloading IMAGES_PER_CLASS images for each class
import os
import io
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image

#Path to chromedriver
PATH = "/home/parac3lsus/chromedriver"
driver = webdriver.Chrome(PATH)

IMAGES_FOLDER = "./Images/"
CLASSES_SEARCH = ['street','city','landscape','people','portrait','animal','house','nature','building']
IMAGES_PER_CLASS = 50
CURRENT_IMAGE_INDEX = 0

def download_image(download_path, image_url):
    global CURRENT_IMAGE_INDEX
    file_name = f"{CURRENT_IMAGE_INDEX}.jpg"
    try:
        # Open the url image
        image_content = requests.get(image_url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')

        #Check if image size is at least 255 x 255
        if image.size[0] < 255 or image.size[1] < 255:
            print(f"Image size is too small: {image_url}")
            return

        #Resize image to 255 x 255
        image = image.resize((224,224))


        #Create path and save image
        file_path = os.path.join(download_path, file_name)
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
            CURRENT_IMAGE_INDEX += 1
            print("Image sucessfully Downloaded: ", file_name)

    except Exception as e:
        print(f"ERROR - COULD NOT DOWNLOAD {image_url} - {e}")


def get_google_images(wd, delay, max_images, search_key):

    # scroll down to bottom
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    # Load page and assign key we will search for
    wd.get("https://www.google.com/imghp?hl=EN")
    search_box = wd.find_element("xpath","//input[@class='gLFyf gsfi']")
    search_box.send_keys(search_key)

    # Click search
    button = wd.find_element("xpath","//button[@class='Tg7LZd']")
    button.click()
    time.sleep(delay)

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_images:

        scroll_to_end(wd)

        # Get all image thumbnail results
        thumbnail_results = wd.find_elements(By.CLASS_NAME,"Q4LuWd")
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # Try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(delay)
            except Exception:
                continue

            # Extract image urls
            actual_images = wd.find_elements(By.CLASS_NAME,'n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_images:
                print(f"Found: {len(image_urls)} image links, done!")
                break
            else:
                print("Found:", len(image_urls), "image links, looking for more ...")
                time.sleep(delay)
                load_more_button = wd.find_element("xpath","//input[@class='mye4qd']")
                if load_more_button:
                    wd.execute_script("document.querySelector('.mye4qd').click();")

        # Move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

def download_urls(urls, delay=0.5):
    for url in urls:
        download_image(IMAGES_FOLDER, url)
        time.sleep(delay)

for img_class in CLASSES_SEARCH:
    print("##############################################")
    print(f"Searching for: {img_class}")
    print("##############################################")
    urls = get_google_images(driver, 0.5, IMAGES_PER_CLASS, img_class)
    download_urls(urls)