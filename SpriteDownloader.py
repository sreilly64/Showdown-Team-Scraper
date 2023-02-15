import sys
import logging
import requests
import os
from pathlib import Path
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


#This script is for downloading missing Pokemon sprite files from Showdown for use by Babiri
class SpriteDownloader:

    base_download_location = os.environ['spriteFolderLocation']  # set 'spriteFolderLocation' in environment variables to the sprites folder of the Babiri front end
    sprite_folder_url = "https://play.pokemonshowdown.com/sprites/dex/"

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
        self.driver_path = "S:\Program Files\ChromeDriver\chromedriver.exe"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")

    def get_missing_sprites(self):
        driver = webdriver.Chrome(options=self.options, service=Service(ChromeDriverManager().install()))
        logging.info("Loading page...")
        driver.get(self.sprite_folder_url)
        # get all <a> where the href is the download url for each sprite
        # if that sprite is not in download location
        # then use requests to download sprite to download location
        try:
            png_download_links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'png')]"))
            )
            logging.info(f"Number of download links: {len(png_download_links)}")

            for png_link in png_download_links:
                download_location = self.base_download_location + f"{png_link.text}"
                path = Path(download_location)
                if not path.is_file() and "totem" not in png_link.text and "vivillon" not in png_link.text and "furfrou" not in png_link.text:
                    logging.info(f"{png_link.text} was not found in project")
                    sprite_data = requests.get(str(png_link.get_attribute("href"))).content
                    with open(f'{download_location}', 'wb') as handler:
                        handler.write(sprite_data)
                    logging.info(f"{png_link.text} saved.")

                    image = Image.open(download_location)
                    resized_image = image.resize((96, 96))
                    resized_image.save(download_location)
                    logging.info(f"{png_link.text} was resized.")
        except TimeoutException:
            logging.error("Timeout Exception occurred, could not find sprite links.")
        except:
            logging.error("Unexpected error when trying to open the login page: %s", sys.exc_info()[0])

        driver.quit()


def main():
    SpriteDownloader().get_missing_sprites()


if __name__ == '__main__':
    main()
