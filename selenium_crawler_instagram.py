from selenium.webdriver.common.keys import Keys
import time
from ./InstaRaider import InstaRaider


class Crawler:
    def __init__(self):
        self.binary = FirefoxBinary('/home/mitrandir/firefox/firefox')
        self.driver = webdriver.Firefox(firefox_binary=self.binary)
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Accept-Language'] = 'en-EN'
        #self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1280, 600)
        self.driver.get("https://www.instagram.com/accounts/login/")
        self.uname = self.wait_for_visibility("username", find_by_name=True)
        self.uname.clear()
        self.uname.send_keys("ste6834")
        self.pswd = self.wait_for_visibility("password", find_by_name=True)
        self.pswd.clear()
        self.pswd.send_keys("stew7171")
        self.wait_for_visibility("_ah57t").click()
        time.sleep(1)
        print "Object Crawler is initialized"

    def screenshot(self):
        self.driver.save_screenshot(str(time.time()) + ".png")

    def wait_for_visibility(self, selector, timeout_seconds=10, one=True, find_by_name=False):
        retries = timeout_seconds
        while retries:
            try:
                if one:
                    if find_by_name is False:
                        element = self.driver.find_element_by_class_name(selector)
                        if element.is_displayed():
                            return element
                    if find_by_name is True:
                        element = self.driver.find_element_by_name(selector)
                        if element.is_displayed():
                            return element
                else:
                    element = self.driver.find_elements_by_class_name(selector)
                    if len(element) > 0:
                        if element[1].is_displayed():
                            return element
            except (NoSuchElementException,
                    StaleElementReferenceException):
                self.screenshot()
                if retries <= 0:
                    raise
                else:
                    pass

            retries = retries - 1
            time.sleep(0.5)
        raise ElementNotVisibleException(
            "Element %s not visible despite waiting for %s seconds" % (
                selector, timeout_seconds)
        )


def validate_length(st):
    print st
    if st.find(",", 0, len(st)) != -1:
        index = st.index(",", 0, len(st) - 1)
        st = st[0:index] + st[index + 1:len(st)]
    if st.isdigit():
        return int(st)
    if st[len(st) - 1] == "k":
        st = st[0:len(st) - 1]
        return int(float(st)) * 1000
    if st[len(st) - 1] == "m":
        st = st[0:len(st) - 1]
        return int(float(st)) * 1000000


def get_followers(username, craw):
    craw.driver.get(username)
    if not is_public(craw):
        return None

    posts_followers_following = craw.wait_for_visibility("_s53mj", one=False)

    length_str = posts_followers_following[1].text.split()[0]
    print "Total " + length_str + " followers"
    length = validate_length(length_str)
    print length

    if length == 0:
        print "0 followers"
        return None

    posts_followers_following[1].click()

    div = craw.wait_for_visibility("_4gt3b")
    div.click()
    current_folls = ['sdf']
    x = 0
    y = 0

    while (len(current_folls) < (length - 10)):
        if len(current_folls) >= 200:
            break
        div.send_keys(Keys.END)
        time.sleep(0.3)
        div.click()
        current_folls = craw.wait_for_visibility("_5lote", one=False)

        if len(current_folls) == x:
            y += 1
            if y == 20:
                break
        x = len(current_folls)
        print x

    ar = []

    for f in current_folls:
        ar.append(f.get_attribute("href"))

    return ar


def is_public(craw):
    html = craw.driver.page_source
    if 'is_private": true' in html:
        print "PRIVATE"
        return False
    if "Sorry, this page isn't available" in html:
        print "Accaunt deleted"
        return False
    else:
        print "PUBLIC"
        return True


def start_crawl(d):
    raid = InstaRaider('', '', num_to_download=10)

    arr = []
    arr.append("https://www.instagram.com/instagram/")
    mas = []
    r = redis.Redis('localhost')
    length_arr = 0
    # cursor = 0
    dummy = '0'
    while True:
        #dummy, arr = r.scan(cursor=length_arr)
        for a in arr:
            length_arr += len(arr)
            print a
            hm = get_followers(a, d)
            if hm == None:
                continue
            else:
                # mas += hm
                #print a + "      !!!!!!!!!!!!!!!!!!!!"
                for i in hm:
                    raid.set_acc(i, './images/' + a[26:], 10)
                    if not raid.validate():
                        print "Not valid"
                    raid.download_photos()
                    raid.download_videos()

crawler = Crawler()
start_crawl(crawler)
