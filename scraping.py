from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import numpy as np
import json

def wait(secs: int = 3):
    """Function to wait for specified number of seconds"""
    time.sleep(secs)

# Setting up the Selenium web driver --- running headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# Array to store data
data = {}

# Url(s) to scrape data from (by season)
urls = [
"https://www.flashscore.com.ng/football/england/premier-league-2024-2025/results/",
"https://www.flashscore.com.ng/football/england/premier-league-2023-2024/results/",
# "https://www.flashscore.com.ng/football/england/premier-league-2022-2023/results/",
# "https://www.flashscore.com.ng/football/england/premier-league-2021-2022/results/",
]
# url = "https://www.flashscore.com.ng/football/england/premier-league-2023-2024/results/"
for url in urls:
    driver.get(url)
    wait()

    # Get the page source
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    current_season = soup.find("div", class_="heading__info").getText()
    data[current_season] = []

    while True:
        try:
            # Find the more matches toggle link
            more_matches = driver.find_element(By.CLASS_NAME, "event__more--static")
            more_matches.send_keys(Keys.ENTER)
            print("Toggling for more matches...")
            wait()
        except Exception as e:
            print("\nNo more pages to toggle", e)
            break

    # Update the page content and pass into bs4
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    try:
        print("Probably no more matches to toggle ----- stopping")
        print("\nAttempting to scrape all matches now")

        # Find all matches for the current season
        matches = soup.find_all("div", class_="event__match--withRowLink")
        match_list = [match for match in matches]
        for match in match_list:
            match_link = match.find("a").get("href")
            match_date = match.find("div", class_="event__time").getText()
            # print(match_date, match_link)

            # Open a new window for the news article
            driver.execute_script(f"window.open('{match_link}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            wait()
            try:
                # Get the current page content
                match_html = driver.page_source
                match_soup = BeautifulSoup(match_html, "html.parser")
                wait()

                # Get the match data
                home_team = (match_soup.find("div", class_="duelParticipant__home")
                             .find("a", class_="participant__participantName").getText())
                away_team = (match_soup.find("div", class_="duelParticipant__away")
                             .find("a", class_="participant__participantName").getText())
                match_score = match_soup.find("div", class_="detailScore__wrapper").getText().split("-")
                home_team_score, away_team_score = match_score[0], match_score[1]

                print("Home:", home_team, "\nAway:", away_team, "\nHome:", home_team_score, "\nAway:", away_team_score)
                print("-" * 50)

                # Navigate to the stats tab and select it
                stats_tab = driver.find_element(By.XPATH, '//*[@id="detail"]/div[7]/div/a[2]/button')
                stats_tab.send_keys(Keys.ENTER)

                # Compile and add the data for the current match into the data array
                match_data = {
                    "match_date": match_date or np.nan,
                    "home_team": home_team or np.nan,
                    "home_team_score": home_team_score or np.nan,
                    "away_team": away_team or np.nan,
                    "away_team_score": away_team_score or np.nan,
                    "season": current_season
                }
                data[current_season].append(match_data)

                # Close the current tab and switch back to the original window
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print("Error accessing match details ---", e)
    except Exception as e:
        print("error:", e)

# Writing the data into a json file...
with open("pl-data.json", "w") as file:
    json.dump(data, file, indent=4)
