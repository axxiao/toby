from selenium import webdriver

driver = webdriver.Firefox()


def build_url(address,username=None,password=None):
    if username and password:
        cred = '://'+username+':'+password+'@'
        url=address.replace('://', cred)
        if url[-1] != '/':
            url += '/'
    else:
        url=address
    return url


def open_web(url, username, password):
    driver.get(build_url(url, username, password))


def get_screenshot():
    return driver.get_screenshot_as_png()