from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
from selenium.common.exceptions import StaleElementReferenceException
import urllib.request
import cloudinary.uploader

cloudinary.config(
  cloud_name = os.getenv("CLOUD_NAME"),
  api_key = os.getenv("API_KEY"),
  api_secret = os.getenv("API_SECRET")
)
options = Options()
options.page_load_strategy = 'none'
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
url = "https://www.depop.com/purevintage_clothing/"
# driver = webdriver.Chrome()
driver.get(url)

# Loop through transactions and count
links = driver.find_elements_by_tag_name('a')


d = 0
while d < 30:
    descriptions = []
    images = []
    pNumbers = []
    product = {}
    def insertIntoDb(p):
        client = MongoClient(
            os.getenv("MONGO_URL"))

        db = client.ecom_mobile

        result = db.products.insert_one(p)

        # Step 4: Print to the console the ObjectID of the new document
        print('Created {0} of 500 as {1}', result.inserted_id)
        driver.back()


    try:
        def getProductInfo():
            driver1 = webdriver.Chrome(options=options)
            driver1.get(driver.current_url)

            desc = driver1.find_elements_by_tag_name("p")

            print(driver1.current_url)

            acts = ActionChains(driver1)

            acts.send_keys(Keys.PAGE_DOWN).perform()


            for a in desc:
                if str(a.get_attribute("data-testid")) == "product__description":
                    # for getting the product name
                    itemNumber = a.text.find("Item number:")
                    fullText = a.text
                    titleStart = fullText.split("\n", 1)[0]
                    try:
                        size = fullText.split("Size ", 1)[1]
                        singleSize = size.split("\n", 1)[0]
                        product['size'] = singleSize

                    except:
                        print("desc issue")
                        continue
                    number = a.text[itemNumber:itemNumber + 18]
                    singleNumber = number.split(":", 1)[1].strip() or "numberwang\nWang"

                    r = open("productNums.txt", "r")
                    print(singleNumber.split("\n", 1)[0])
                    for line in r:
                        print(line)
                        if singleNumber.split("\n", 1)[0] in line:
                            print("item dupe")
                            continue

                    # print(singleNumber)
                    product['index'] = singleNumber.split("\n", 1)[0]
                    f = open("productNums.txt", "a")
                    f.write(singleNumber.split("\n", 1)[0] + "\n")
                    f.close()
                    product['name'] = titleStart
                    product['description'] = fullText.split("Item", 1)[0]

            img = driver1.find_elements_by_tag_name("img")
            for i in range(len(img)):
                im = driver1.find_elements_by_tag_name("img")[i]
                if str(im.get_attribute("data-testid")) == "lazyLoadImage__img":
                    imSrc = im.get_attribute("src")
                    print(imSrc)
                    if imSrc is not None:
                        images.append(imSrc)

            print(images)
            it = 0
            ot = 0
            n = product['name']
            for ima in images:
                print(ima)
                newName = n + str(it)
                newName = newName + ".jpg"
                print(newName)
                try:
                    urllib.request.urlretrieve(ima,"./imgs/"+ newName.replace("/", ""))
                    it += 1
                except Exception as e:
                    it +=1
                    print("images issue")
                    print(e)
                    continue
            #     print(ima)

            print(images)
            cloudImages = []
            for k in range(4):
                newName = n + str(k)
                newName = newName + ".jpg"

                c = cloudinary.uploader.upload("./imgs/" + newName.replace("/", ""),
                                               width=1250,
                                               height=1250,
                                               tags="pure-vintage",
                                               public_id=newName.replace("/", ""))
                print(c)
                cloudImages.append(c['url'])
                ot += 1

            print(cloudImages)
            product['image'] = cloudImages[:4]
            price = driver1.find_elements_by_tag_name("span")
            for p in price:
                if str(p.get_attribute("aria-label")) == "Price" or str(p.get_attribute("aria-label")) == "Discounted Price":
                    # print(p.text)
                    product['price'] = int(p.text[1:-3])

            brands = ['gap', 'ralph', 'nike', 'fila', 'north', 'tommy', 'burberry', 'reebok', 'adidas', 'carhartt',
                      'helly', 'ysl', "dior",'lacoste', 'kappa', 'champion', 'umbro', 'levi', "calvin", "guess", "puma",
                      "valentino", "berghaus"]
            for brand in brands:
                lower = product['name'].lower()
                if lower.find(brand):
                    # print(brand)
                    e = lower.split(" ")
                    for q in e:
                        if q == brand:
                            # print(brand)
                            product['brand'] = q

                else:
                    product['brand'] = "n/a"
                    print("no brand")
                    continue
            # print(product)
            categories = ['jeans', 'coat', 'shirt', 't-shirt', 'trousers', 'track', 'fleece', 'hat', 'puffer',
                          'blazer', "polo", "tracksuit",
                          'joggers', 'shorts', 'windbreaker', "cap", "hat", "track jacket", "harrington", "sweatshirt",
                          "football", "necklace", "hoodie"]
            for category in categories:
                lower = product['name'].lower()
                if lower.find(category):
                    # print(category)
                    e = lower.split(" ")
                    for q in e:

                        if q == category:
                            print(q)
                            if q == "fleece":
                                product['category'] = "fleeces"
                            elif q == "cap":
                                product['category'] = "caps"
                            elif q == "track jacket":
                                product['category'] = "trackjack"
                            elif q == "tracksuit":
                                product['category'] = "tracksuits"
                            elif q == "hat":
                                product['category'] = "hats"
                            elif q == "coat":
                                product['category'] = "coats"
                            elif q == "shirt":
                                product['category'] = "shirts"
                            elif q == "sweatshirt":
                                product['category'] = "sweatshirts"
                            elif q == "t-shirt":
                                product['category'] = "t-shirts"
                            elif q == "blazer":
                                product['category'] = "blazers"
                            elif q == "coat":
                                product['category'] = "coats"
                            elif q == "necklace":
                                product['category'] = "necklaces"
                            elif q == "polo":
                                product['category'] = "polos"
                            elif q == "hoodie":
                                product['category'] = "hoodies"
                            elif q == "windbreaker":
                                product['category'] = "windbreakers"
                            else:
                                print(category)
                                product['category'] = q

                            break

                else:
                    product['category'] = "n/a"
                    print("no cat")

            product["inStock"] = True
            product['featured'] = False
            product['createdAt'] = datetime.now()
            product['updatedAt'] = datetime.now()
            product['rating'] = 5
            product['numReviews'] = 0
            product['reviews'] = []

            print(product)

            try:

                print("about to insert")
                if product is not None:
                    insertIntoDb(product)

            except Exception as e:
                print("nisert product")
                print(e)

        li = []
        for t in range(len(links)):
            try:
                link = driver.find_elements_by_tag_name("a")[t]
                linkClass = link.get_attribute("class")

                if str(linkClass[:19]) == "styles__ProductCard":
                    li.append(link)

            except:
                continue

        t = 0
        for i in range(len(li)):
            print(len(links))
            # print(i.get_attribute("class"))
            print(i)
            # try:
            link = driver.find_elements_by_tag_name("a")[i]
            linkClass = link.get_attribute("class")

            if str(linkClass[:19]) == "styles__ProductCard":
                print(linkClass)
                action = ActionChains(driver)
                action.move_to_element(link)

                action.click().perform()
                getProductInfo()

    except Exception as e:
        print(e)
        print("error down here")
        driver.back()

        continue

    d+=1









