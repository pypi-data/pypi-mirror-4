
from ghost import Ghost


def take_screenshot_of_url(url, target_filename):
    ghost = Ghost()
    page, resources = ghost.open(url)
    ghost.capture_to(target_filename)


def take_screenshot_of_page(page, target_filename):
    take_screenshot_of_url(page.url, target_filename)
