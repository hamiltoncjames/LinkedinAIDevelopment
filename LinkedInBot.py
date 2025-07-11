#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Matt Flood

import os
import random
import sys
import time
from urllib.parse import urlparse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from random import shuffle
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


# Configurable Constants
EMAIL = os.getenv("EMAIL", '')
PASSWORD = os.getenv("PASSWORD", '')
VIEW_SPECIFIC_USERS = False
SPECIFIC_USERS_TO_VIEW = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE = 5
CONNECT_WITH_USERS = True
RANDOMIZE_CONNECTING_WITH_USERS = True
JOBS_TO_CONNECT_WITH = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
ENDORSE_CONNECTIONS = False
RANDOMIZE_ENDORSING_CONNECTIONS = True
VERBOSE = True

# Configurable Output Fields (comma-separated, e.g., 'name,email,phone')
OUTPUT_FIELDS = os.getenv("OUTPUT_FIELDS", 'url,name,connection_degree,country,email,phone')
MAX_PROFILE_VIEWS = int(os.getenv("MAX_PROFILE_VIEWS", 1000))
PROFILE_DATA_DIR = 'profile_data'


def Launch():
    """
    Launch the LinkedIn bot.
    """

    # Check if the file 'visitedUsers.txt' exists, otherwise create it
    if os.path.isfile('visitedUsers.txt') == False:
        visitedUsersFile = open('visitedUsers.txt', 'wb')
        visitedUsersFile.close()

    # Browser choice
    print('Choose your browser:')
    print('[1] Chrome')
    print('[2] Firefox/Iceweasel')
    print('[3] PhantomJS')

    while True:
        try:
            browserChoice = int(input('Choice? '))
        except ValueError:
            print('Invalid choice.'),
        else:
            if browserChoice not in [1, 2, 3]:
                print('Invalid choice.'),
            else:
                break

    StartBrowser(browserChoice)


def StartBrowser(browserChoice):
    """
    Launch broswer based on the user's selected choice.
    browserChoice: the browser selected by the user.
    """

    if browserChoice == 1:
        print('\nLaunching Chrome')
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    elif browserChoice == 2:
        print('\nLaunching Firefox/Iceweasel')
        browser = webdriver.Firefox()

    elif browserChoice == 3:
        print('\nLaunching PhantomJS')
        browser = webdriver.PhantomJS()

    # Sign in
    browser.get('https://linkedin.com/uas/login')
    emailElement = browser.find_element(By.ID, 'username')
    emailElement.send_keys(EMAIL)
    passElement = browser.find_element(By.ID, 'password')
    passElement.send_keys(PASSWORD)
    passElement.submit()

    print('Signing in...')
    time.sleep(3)

    # Extract own profile URL after login
    browser.get('https://www.linkedin.com/feed/')
    time.sleep(2)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    own_profile_url = extract_own_profile_url(soup)
    print(f"Your profile URL: {own_profile_url}")

    soup = BeautifulSoup(browser.page_source, "html.parser")
    if soup.find('div', {'class': 'alert error'}):
        print('Error! Please verify your username and password.')
        browser.quit()
    elif browser.title == '403: Forbidden':
        print('LinkedIn is momentarily unavailable. Please wait a moment, then try again.')
        browser.quit()
    else:
        print('Success!\n')
        LinkedInBot(browser, own_profile_url)


def LinkedInBot(browser, own_profile_url):
    """
    Run the LinkedIn Bot.
    browser: the selenium driver to run the bot with.
    own_profile_url: the user's own profile URL to skip.
    """
    import csv
    import os
    from datetime import datetime
    if not os.path.exists(PROFILE_DATA_DIR):
        os.makedirs(PROFILE_DATA_DIR)
    visited_profiles = set()
    error_log_path = 'errorLog.csv'
    # Write error log header if not exists
    if not os.path.exists(error_log_path):
        with open(error_log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'error'])
    print('At the home page to scrape user urls..\n')
    while len(visited_profiles) < MAX_PROFILE_VIEWS:
        try:
            NavigateToHomePage(browser)
            time.sleep(2)
            soup = BeautifulSoup(browser.page_source, "html.parser")
            profile_links = extract_home_feed_profile_links(soup)
            new_profiles = [link for link in profile_links if link not in visited_profiles and link != own_profile_url]
            if not new_profiles:
                ScrollToBottomAndWaitForLoad(browser)
                continue
            for profile_url in new_profiles:
                if len(visited_profiles) >= MAX_PROFILE_VIEWS:
                    print(f"Reached {MAX_PROFILE_VIEWS} profile views. Exiting gracefully.")
                    return
                print(f"Visiting profile: {profile_url}")
                visited_profiles.add(profile_url)
                browser.get('https://www.linkedin.com' + profile_url)
                time.sleep(random.uniform(2, 3))
                # Extract and save profile data
                profile_soup = BeautifulSoup(browser.page_source, "html.parser")
                profile_data = extract_profile_data(profile_url, profile_soup)
                save_profile_data(profile_data)
                browser.back()
                time.sleep(2)
            ScrollToBottomAndWaitForLoad(browser)
            print(f"Visited {len(visited_profiles)} unique profiles this session.")
        except Exception as e:
            with open(error_log_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), str(e)])
            print(f"Error occurred: {e}. Logged to {error_log_path}")
    print(f"Graceful shutdown after visiting {MAX_PROFILE_VIEWS} profiles.")


def NavigateToHomePage(browser):
    """
    Navigate to the LinkedIn home page and scroll to the bottom to load more content.
    browser: the selenium browser used to interact with the page.
    """
    browser.get('https://www.linkedin.com/feed/')
    for counter in range(1, NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE):
        ScrollToBottomAndWaitForLoad(browser)


def ConnectWithUser(browser):
    """
    Connect with the user viewing if their job title is found in your list of roles
    you want to connect with.
    browse: the selenium browser used to interact with the page.
    """

    soup = BeautifulSoup(browser.page_source, "html.parser")
    jobTitleMatches = False

    # I know not that efficient of a loop but BeautifulSoup and Selenium are
    # giving me a hard time finding the specifc h2 element that contain's user's job title
    for h2 in soup.find_all('h2'):
        for job in JOBS_TO_CONNECT_WITH:
            if job.upper() in h2.getText().upper():
                jobTitleMatches = True
                break

    if jobTitleMatches:
        try:
            if VERBOSE:
                print('Sending the user an invitation to connect.')
                # old class = connect primary top-card-action ember-view
                browser.find_element(By.XPATH,
                    '//button[@class="pv-s-profile-actions pv-s-profile-actions--connect ml2 artdeco-button artdeco-button--2 artdeco-button--primary ember-view"]').click()
                time.sleep(random.randrange(3))
                browser.find_element(By.XPATH,
                    '//button[@class="ml1 artdeco-button artdeco-button--3 artdeco-button--primary ember-view"]').click()
        except:
            pass


def GetNewProfileURLS(soup, profilesQueued):
    """
    Get new profile urls to add to the navigate queue.
    soup: beautiful soup instance of page's source code.
    profileQueued: current list of profile queues.
    """

    # Open, load and close
    with open('visitedUsers.txt', 'r') as visitedUsersFile:
        visitedUsers = [line.strip() for line in visitedUsersFile]
    visitedUsersFile.close()

    profileURLS = []
    profileURLS.extend(FindProfileURLsInNetworkPage(
        soup, profilesQueued, profileURLS, visitedUsers))
    profileURLS.extend(FindProfileURLsInPeopleAlsoViewed(
        soup, profilesQueued, profileURLS, visitedUsers))
    profileURLS.extend(FindProfileURLsInEither(
        soup, profilesQueued, profileURLS, visitedUsers))
    profileURLS = list(set(profileURLS))

    return profileURLS


def FindProfileURLsInNetworkPage(soup, profilesQueued, profileURLS, visitedUsers):
    """
    Get new profile urls to add to the navigate queue from the my network page.
    soup: beautiful soup instance of page's source code.
    profileQueued: current list of profile queues.
    profileURLS: profile urls already found this scrape.
    visitedUsers: user's profiles that we have already viewed.
    """

    newProfileURLS = []

    try:
        for a in soup.find_all('a', class_='discover-entity-type-card__link'):
            if ValidateURL(a['href'], profileURLS, profilesQueued, visitedUsers):

                if VIEW_SPECIFIC_USERS:
                    for span in a.find_all('span', class_='discover-person-card__occupation'):
                        for occupation in SPECIFIC_USERS_TO_VIEW:
                            if occupation.lower() in span.text.lower():
                                if VERBOSE:
                                    print(a['href'])
                                newProfileURLS.append(a['href'])
                                break

                else:
                    if VERBOSE:
                        print(a['href'])
                    newProfileURLS.append(a['href'])
    except:
        pass

    return newProfileURLS


def FindProfileURLsInPeopleAlsoViewed(soup, profilesQueued, profileURLS, visitedUsers):
    """
    Get new profile urls to add to the navigate queue from the people also viewed section.
    soup: beautiful soup instance of page's source code.
    profileQueued: current list of profile queues.
    profileURLS: profile urls already found this scrape.
    visitedUsers: user's profiles that we have already viewed.
    """

    newProfileURLS = []

    try:
        for a in soup.find_all('a', class_='pv-browsemap-section__member'):
            if ValidateURL(a['href'], profileURLS, profilesQueued, visitedUsers):

                if VIEW_SPECIFIC_USERS:
                    for div in a.find_all('div'):
                        for occupation in SPECIFIC_USERS_TO_VIEW:
                            if occupation.lower() in div.text.lower():
                                if VERBOSE:
                                    print(a['href'])
                                newProfileURLS.append(a['href'])
                                break

                else:
                    if VERBOSE:
                        print(a['href'])
                    newProfileURLS.append(a['href'])
    except:
        pass

    return newProfileURLS


def FindProfileURLsInEither(soup, profilesQueued, profileURLS, visitedUsers):
    """
    Get new profile urls to add to the navigate queue, some use different class
    names in the my network page and people also viewed section.
    soup: beautiful soup instance of page's source code.
    profileQueued: current list of profile queues.
    profileURLS: profile urls already found this scrape.
    visitedUsers: user's profiles that we have already viewed.
    """

    newProfileURLS = []

    try:
        for ul in soup.find_all('ul', class_='pv-profile-section__section-info'):
            for li in ul.find_all('li'):
                a = li.find('a')
                if ValidateURL(a['href'], profileURLS, profilesQueued, visitedUsers):

                    if VIEW_SPECIFIC_USERS:
                        for div in a.find_all('div'):
                            for occupation in SPECIFIC_USERS_TO_VIEW:
                                if occupation.lower() in div.text.lower():
                                    if VERBOSE:
                                        print(a['href'])
                                    profileURLS.append(a['href'])
                                    break

                    else:
                        if VERBOSE:
                            print(a['href'])
                        profileURLS.append(a['href'])
    except:
        pass

    return newProfileURLS


def ValidateURL(url, profileURLS, profilesQueued, visitedUsers):
    """
    Validate the url passed meets requirement to be navigated to.
    profileURLS: list of urls already added within the GetNewProfileURLS method to be returned.
        Want to make sure we are not adding duplicates.
    profilesQueued: list of urls already added and being looped. Want to make sure we are not
        adding duplicates.
    visitedUsers: users already visited. Don't want to be creepy and visit them multiple days in a row.
    """

    return url not in profileURLS and url not in profilesQueued and "/in/" in url and "connections" not in url and "skills" not in url and url not in visitedUsers


def EndorseConnections(browser):
    """
    Endorse skills for your connections found. This only likes the top three popular
    skills the user has endorsed. If people want this feature can be further
    expanded just post an enhancement request in the repository.
    browser:
    """

    print("Gathering your connections url's to endorse their skills.")
    profileURLS = []
    browser.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(3)

    try:
        for counter in range(1, NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE):
            ScrollToBottomAndWaitForLoad(browser)

        soup = BeautifulSoup(browser.page_source, "html.parser")
        for a in soup.find_all('a', class_='mn-person-info__picture'):
            if VERBOSE:
                print(a['href'])
            profileURLS.append(a['href'])

        print("Endorsing your connection's skills.")

        for url in profileURLS:

            endorseConnection = True
            if RANDOMIZE_ENDORSING_CONNECTIONS:
                endorseConnection = random.choice([True, False])

            if endorseConnection:
                fullURL = 'https://www.linkedin.com'+url
                if VERBOSE:
                    print('Endorsing the connection '+fullURL)

                browser.get(fullURL)
                time.sleep(3)
                for button in browser.find_elements_by_xpath('//button[@data-control-name="endorse"]'):
                    button.click()
    except:
        print('Exception occurred when endorsing your connections.')
        pass

    print('')


def ScrollToBottomAndWaitForLoad(browser):
    """
    Scroll to the bottom of the page and wait for the page to perform it's lazy loading.
    browser: selenium webdriver used to interact with the browser.
    """

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)


def extract_home_feed_profile_links(soup):
    """
    Extract unique user profile links from the LinkedIn home feed.
    """
    profile_links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/in/') and '?' not in href:
            profile_links.add(href)
    return list(profile_links)


def extract_own_profile_url(soup):
    """
    Extract the user's own profile URL from the LinkedIn home page soup.
    """
    # Look for the 'Me' link in the top nav
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/in/') and 'mini-profile' in str(a.get('class', '')):
            return href
    # Fallback: first /in/ link
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/in/'):
            return href
    return None


def extract_profile_data(profile_url, soup):
    """
    Extract profile data fields as specified in OUTPUT_FIELDS.
    """
    data = {'url': 'https://www.linkedin.com' + profile_url}
    if 'name' in OUTPUT_FIELDS:
        name_tag = soup.find('h1')
        data['name'] = name_tag.get_text(strip=True) if name_tag else 'N/A'
    if 'connection_degree' in OUTPUT_FIELDS:
        # Look for 1st, 2nd, 3rd, etc. near the top of the profile
        degree_tag = soup.find(lambda tag: tag.name in ['span', 'div'] and tag.get_text(strip=True) in ['1st', '2nd', '3rd', '4th'])
        data['connection_degree'] = degree_tag.get_text(strip=True) if degree_tag else 'N/A'
    if 'country' in OUTPUT_FIELDS:
        # Look for location, usually in a span or li near the top
        country_tag = soup.find(lambda tag: tag.name in ['span', 'li'] and (',' in tag.get_text(strip=True) or 'United' in tag.get_text(strip=True)))
        data['country'] = country_tag.get_text(strip=True) if country_tag else 'N/A'
    if 'email' in OUTPUT_FIELDS:
        data['email'] = 'N/A'  # Email is not public on most profiles
    if 'phone' in OUTPUT_FIELDS:
        data['phone'] = 'N/A'  # Phone is not public on most profiles
    return data


def save_profile_data(profile_data):
    """
    Save profile data to a CSV file in the profile_data directory.
    """
    import csv
    import os
    file_path = os.path.join(PROFILE_DATA_DIR, 'profiles.csv')
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=profile_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(profile_data)


if __name__ == '__main__':
    Launch()
