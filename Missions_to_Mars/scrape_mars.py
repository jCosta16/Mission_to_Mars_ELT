# Dependencies
import requests
from bs4 import BeautifulSoup
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import pandas as pd
import selenium.webdriver as webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep 

from flask import Flask, jsonify, render_template
import pymongo


def scrape():
# Scraping News

    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    # URL of page to be scraped
    url_news = "https://mars.nasa.gov/news/"
    browser.visit(url_news)
    html_news = browser.html
    # Create BeautifulSoup object; parse with 'html.parser'
    soup_news = BeautifulSoup(html_news, 'html.parser')
    news_title = soup_news.find('div', class_='content_title').find('a').text
    news_p = soup_news.find('div', class_='article_teaser_body').text
    browser.quit()
    mars_news = {"news_title":news_title, "news_p": news_p}

    # Scraping featured image (image, alt)
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    url_img = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_img)
    html_img = browser.html
    soup_img = BeautifulSoup(html_img, 'html.parser')
    img_grid = soup_img.find('article', class_='carousel_item')
    img_alt =  img_grid.h1.text.strip()
    feat_img = img_grid.a['data-fancybox-href']
    feat_img = "https://www.jpl.nasa.gov" + feat_img
    featured_img = {'img_alt':img_alt, 'url':feat_img}
    browser.quit()

    
    # Scraping Weather
    url_weather = 'https://twitter.com/marswxreport?lang=en'
    response_weather = requests.get(url_weather)
    soup_weather = BeautifulSoup(response_weather.text, 'lxml')
    mars_weather = soup_weather.find('p', class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text.strip()
    mars_weather = mars_weather.split(" hPapic")[0]
    mars_weather = mars_weather.replace("\n", ", ")

    # Scraping Facts
    url_facts = 'https://space-facts.com/mars/'
    tables_facts = pd.read_html(url_facts)
    table_mars = pd.DataFrame(tables_facts[0])
    table_mars.columns = ["Data", "Value"]
    mars_html_table = table_mars.to_html(index=False)

    # Scraping Hemispheres (title, image url)
    browser = webdriver.Chrome()
    browser.get('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    all_elements = ui.WebDriverWait(browser, 15).until(lambda browser: browser.find_elements_by_class_name('item'))

    hemis_title = []
    hemis_img = []
    main_window = browser.current_window_handle

    for element in all_elements:
        hemis_name = element.find_element_by_tag_name("h3").text
        hemis_name = hemis_name.split(" Enhanced")[0]
        hemis_title.append(hemis_name) 
        
        first_link = element.find_element_by_tag_name('a')

        # Open the link in a new tab by sending key strokes on the element
        first_link.send_keys(Keys.CONTROL + Keys.SHIFT + Keys.RETURN)

        # Switch tab to the new tab
        handle = browser.window_handles[-1]
        
        try:     
            browser.switch_to.window(handle)

            link = browser.find_element_by_class_name('downloads')
            hemis_href = link.find_element_by_tag_name('a').get_attribute('href')
            hemis_img.append(hemis_href)

        except:
            print(f"Error on tab {handle}")
            
        browser.switch_to.window(main_window)
            
    browser.quit()        

    # create a list of dictionaries
    hemisphere_image_urls = []
    count = 0
    for image in hemis_img:
        img_dic= {}
        img_dic["title"] = hemis_title[count]
        img_dic["img_url"] = image
        hemisphere_image_urls.append(img_dic)
        count = count+1

    mars = {
        "news_title":news_title, 
        "news_p": news_p,
        "featured_img": featured_img,
        "mars_weather" : mars_weather,
        "mars_facts": mars_html_table,
        "hemisphere": hemisphere_image_urls
    }
 


    return mars
