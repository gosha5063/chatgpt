# import json
# from time import sleep
#
# from selenium import webdriver
# from selenium.webdriver import DesiredCapabilities
# from selenium.webdriver.remote.command import Command
# from webdriver_manager.chrome import ChromeDriverManager
#
#
# def is_active(driver):
#     try:
#         driver.execute(Command.GET_ALL_COOKIES)
#         return True
#     except Exception:
#         return False
#
#
# def get_token():
#     # make chrome log requests
#     capabilities = DesiredCapabilities.CHROME
#     capabilities["loggingPrefs"] = {"performance": "ALL"}
#     capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
#     driver = webdriver.Chrome(desired_capabilities=capabilities,
#                               executable_path=ChromeDriverManager().install())
#     driver.get(
#         "https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d")
#
#     token = None
#
#     while token == None and is_active(driver):
#         sleep(1)
#         try:
#             logs_raw = driver.get_log("performance")
#         except:
#             pass
#
#         for lr in logs_raw:
#             log = json.loads(lr["message"])["message"]
#             url_fragment = log.get('params', {}).get('frame', {}).get('urlFragment')
#
#             if url_fragment:
#                 token = url_fragment.split('&')[0].split('=')[1]
#
#     try:
#         driver.close()
#     except:
#         pass
#
#     return token
#
#
# print(get_token())


token = "AQAAAABUEq_5AAG8XleghLapBUvLj7OPKJ2ooDg"
from yandex_music import Client
client =  Client(token).init()
# h = client.users_playlists_create(title='new_album').kind
# h2 = client.search(text = '"Moon River"  Henry Mancini').best.result.id
h3 = client.users_playlists(kind=1024)
print(h3.track_count)

# h3 = client.search(text = '"Moon River"  Henry Mancini').best.result.albums[0].id
#
# print(client.users_playlists_insert_track(kind=h,track_id = h2,album_id=h3,revision=1))
# client.users_playlists_delete(kind='1004')
# print(client.users_playlists(kind='1006'))
# print(client.users_likes_tracks()[0].fetch_track())