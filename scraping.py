from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

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
data = []

# Url(s) to scrape data from (by season)
url = "https://www.flashscore.com.ng/football/england/premier-league-2023-2024/results/"
driver.get(url)
wait()

# Get the page source
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

while True:
    try:
        # Find the more matches toggle link
        more_matches = driver.find_element(By.CLASS_NAME, "event__more--static")
        more_matches.send_keys(Keys.ENTER)
        print("Toggling for more matches...")
        wait()
    except Exception as e:
        print("\nNo more pages to scrape", e)
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
    for match in match_list[:5]:
        match_link = match.find("a").get("href")
        match_date = match.find("div", class_="event__time").getText()
        print(match_date, match_link)

        # Open a new window for the news article
        driver.execute_script(f"window.open('{match_link}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        wait()
        try:
            # Get the current page content
            match_html = driver.page_source
            match_soup = BeautifulSoup(match_html, "html.parser")

            # Get the match data
            home_team = (match_soup.find("div", class_="duelParticipant__home")
                         .find("a", class_="participant__participantName").getText())
            away_team = (match_soup.find("div", class_="duelParticipant__away")
                         .find("a", class_="participant__participantName").getText())
            match_score = match_soup.find("div", class_="detailScore__wrapper").getText()
            home_team_score, away_team_score = match_score.split("-")[0], match_score.split("-")[1]

            # print("Home:", home_team, "\nAway:", away_team, "\nScore:", match_score)

            # Navigate to the stats tab and select it
            # stats_tab = driver.find_element(By.XPATH, '//*[@id="detail"]/div[7]/div/a[2]/button')
            # stats_tab.send_keys(Keys.ENTER)

            # Compile and add the data for the current match into the data array
            # match_data = {
            #     "match_date": match_date,
            #     "home_team": home_team,
            #     "home_team_score": home_team_score,
            #     "away_team": away_team,
            #     "away_team_score": away_team_score,
            # }
            # data.append(match_data)

            # Close the current tab and switch back to the original window
            # driver.close()
            # driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            print("Error accessing match details ---", e)
except Exception as e:
    print("error:", e)


# duelParticipant__home
#     a --- participant__participantName
# duelParticipant__away
#     a --- participant__participantName
# detailScore__wrapper







#     # matches.extend([game.getText() for game in games])
#     print("Added {} gameweeks to data".format(len(matches)))
# except Exception as e:
#     print("Error scraping gameweeks", e)
#
# print("Number of gameweeks: {}".format(len(matches)))
#
# for gw in matches:
#     print(gw)
#

# //*[@id="detail"]/div[7]/div/a[2]/button
# //*[@id="detail"]/div[7]/div/a[2]/button