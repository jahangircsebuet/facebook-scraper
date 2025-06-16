import time
import traceback
import random
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from browser import Browser
import re
from crawler.login import Login


class PostAndCommentsScraper:
    def __init__(self, browser, depth=1):
        self.browser = browser
        self.depth = depth
        self.data = []
        print("Initialized PostAndCommentsScraper with depth:", depth)

    def scroll_web_page(self):
        try:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolled to bottom")
            time.sleep(random.uniform(2, 4))
            return True
        except Exception as e:
            print(f"Scroll error: {e}")
            return False

    def scroll_comments_popup(self, popup_element, max_scrolls=5):
        for i in range(max_scrolls):
            try:
                print(f"Scrolling comment popup: iteration {i + 1}")
                self.browser.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollHeight', popup_element
                )
                time.sleep(1)
            except Exception as e:
                print(f"Popup scroll error: {e}")
                break

    def extract_commenter_details(self, container=None):
        commenters = []
        try:
            print("Extracting commenter details...")
            search_scope = container if container else self.browser
            comment_divs = search_scope.find_elements(
                By.XPATH, ".//div[@role='article' and starts-with(@aria-label, 'Comment by')]"
            )
            print(f"Found {len(comment_divs)} comment elements")

            for comment_div in comment_divs:
                try:
                    name = ""
                    profile_url = ""
                    comment_text = ""

                    try:
                        name_elem = comment_div.find_element(By.XPATH, ".//a[@role='link' and not(@aria-hidden='true')]")
                        name = name_elem.text.strip()
                        profile_url = name_elem.get_attribute("href")
                    except NoSuchElementException:
                        print("Name or profile link not found for comment")

                    try:
                        text_elem = comment_div.find_element(By.XPATH, ".//div[@dir='auto' and @style]")
                        comment_text = text_elem.text.strip()
                    except NoSuchElementException:
                        print("Comment text not found")

                    if comment_text:
                        commenters.append({
                            "name": name,
                            "profile_url": profile_url,
                            "comment_text": comment_text
                        })
                        print(f"Extracted comment by {name}: {comment_text[:50]}...")
                except Exception as e:
                    print(f"Error extracting commenter info: {e}")

        except Exception as e:
            print(f"Error in extract_commenter_details: {e}")

        return commenters

    def extract_reactions(self):
        reactions = {}
        try:
            print("Extracting reactions...")
            tabs = WebDriverWait(self.browser, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@role='tab']"))
            )
            for tab in tabs:
                label = tab.get_attribute("aria-label")
                if label:
                    match = re.search(r"Show ([\d,]+) (?:person|people) who reacted with (.+)", label)
                    if match:
                        count = int(match.group(1).replace(',', ''))
                        reaction = match.group(2).strip()
                        reactions[reaction] = count
                        print(f"Reaction extracted: {reaction} - {count}")
        except TimeoutException:
            print("Reaction modal not found.")
        return reactions

    def close_specific_popup(self, close_icon_path):
        try:
            close_button = WebDriverWait(self.browser, 5).until(
                EC.element_to_be_clickable((By.XPATH, close_icon_path))
            )
            self.browser.execute_script("arguments[0].click();", close_button)
            print("Closed popup")
            time.sleep(1)
        except TimeoutException:
            print("Close button not found or not clickable")

    def close_reaction_overlay_with_esc(self):
        try:
            actions = ActionChains(self.browser)
            actions.send_keys(Keys.ESCAPE).perform()
            print("Sent ESC key to close reaction overlay")
            time.sleep(1)
        except Exception as e:
            print(f"Failed to send ESC key: {e}")

    def scrape_posts_and_comments(self, url, loginRequired=False, email='', password=''):
        print(f"Starting scrape on URL: {url}")
        if loginRequired:
            login_fb = Login(self.browser)
            login_fb.login(email, password)
            print("Logged in successfully")

        self.browser.get(url)
        print("Page loaded")
        time.sleep(5)

        for i in range(self.depth):
            print(f"Scroll iteration: {i + 1}")
            if not self.scroll_web_page():
                break
            time.sleep(3)

            posts = self.browser.find_elements(By.XPATH, "//div[@data-ad-preview='message']")
            comment_buttons = self.browser.find_elements(
                By.XPATH, "//div[@aria-label='Leave a comment' and @role='button']"
            )
            reaction_buttons = self.browser.find_elements(
                By.XPATH, "//div[@role='button' and .//div[text()='All reactions:']]"
            )

            print(f"Found {len(posts)} posts, {len(comment_buttons)} comment buttons, {len(reaction_buttons)} reaction buttons")

            for idx, post in enumerate(posts):
                reactions = {}
                try:
                    if idx >= len(comment_buttons) or idx >= len(reaction_buttons):
                        continue

                    self.browser.execute_script(
                        "arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", post
                    )
                    time.sleep(1)

                    try:
                        see_more_button = post.find_element(
                            By.XPATH, ".//div[@role='button' and contains(text(),'See more')]"
                        )
                        self.browser.execute_script("arguments[0].click();", see_more_button)
                        print("Clicked 'See more' to expand post")
                        time.sleep(1.5)
                    except NoSuchElementException:
                        pass

                    post_text = post.text.strip().replace('\n', ' ')
                    print(f"Processing post #{idx + 1}: {post_text[:60]}...")

                    reaction_button = reaction_buttons[idx]
                    self.browser.execute_script("arguments[0].click();", reaction_button)
                    print("Clicked 'All reactions' button")
                    time.sleep(2)
                    reactions = self.extract_reactions()
                    self.close_reaction_overlay_with_esc()

                    comment_button = comment_buttons[idx]
                    self.browser.execute_script("arguments[0].click();", comment_button)
                    print("Clicked 'Comment' button")
                    time.sleep(2)

                    comments_modal = WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                    )
                    print("Comments modal opened")

                    try:
                        scrollable = comments_modal.find_element(
                            By.XPATH, ".//div[@data-virtualized='false']"
                        )
                        print("Found scrollable comment container")
                    except NoSuchElementException:
                        scrollable = comments_modal
                        print("Using fallback container for comments")

                    self.scroll_comments_popup(scrollable, max_scrolls=5)

                    comment_details = self.extract_commenter_details(container=comments_modal)
                    print(f"Extracted {len(comment_details)} structured comments")

                    self.data.append({
                        "post": post_text,
                        "comment_details": comment_details,
                        "reactions": reactions
                    })

                    self.close_specific_popup("//div[@aria-label='Close' and @role='button']")

                except (NoSuchElementException, TimeoutException):
                    print(f"Error processing post #{idx + 1}")
                    traceback.print_exc()

        print(f"Finished scraping. Total posts scraped: {len(self.data)}")
        return self.data

    def save_to_csv(self, filename="posts_comments_reactions.csv"):
        max_structured = max(len(entry["comment_details"]) for entry in self.data) if self.data else 0

        header = ["Post", "Reactions"] + \
                 [f"Commenter {i + 1} Name" for i in range(max_structured)] + \
                 [f"Commenter {i + 1} Profile" for i in range(max_structured)] + \
                 [f"Commenter {i + 1} Text" for i in range(max_structured)]

        print("CSV Header:", header)

        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for idx, entry in enumerate(self.data):
                row = [entry["post"], str(entry.get("reactions", {}))]

                names = [cd["name"] for cd in entry["comment_details"]]
                profiles = [cd["profile_url"] for cd in entry["comment_details"]]
                texts = [cd["comment_text"] for cd in entry["comment_details"]]

                row.extend(names + [""] * (max_structured - len(names)))
                row.extend(profiles + [""] * (max_structured - len(profiles)))
                row.extend(texts + [""] * (max_structured - len(texts)))

                print(f"Writing row {idx + 1}: {row[:5]}... + {len(names)} commenters")
                writer.writerow(row)

        print(f"Saved scraped data to {filename}")


if __name__ == "__main__":
    browser = Browser(0).getBrowser()
    scraper = PostAndCommentsScraper(browser=browser, depth=3)

    scraped_data = scraper.scrape_posts_and_comments(
        url="https://www.facebook.com/CricketSarcasmMemes",
        loginRequired=False,
        email="your_email",
        password="your_password",
    )

    scraper.save_to_csv()