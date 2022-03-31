import json
import requests
import re
import time

titles_cache = [0.0, []]


class TitleParser:
    def __init__(self):
        pass

    @staticmethod
    def get_web():
        return requests.get("https://wiki.biligame.com/umamusume/%E7%A7%B0%E5%8F%B7").text

    def parse_web(self):
        data = self.get_web()
        rule = re.compile(r"<tr>(.*?)</tr>", re.S)
        return rule.findall(data)

    @staticmethod
    def check_cache(refresh_time=14400):
        global titles_cache

        if titles_cache[1] is not None:
            time_now = time.time()
            time_cache = titles_cache[0]
            if time_now - time_cache > refresh_time:
                return None
            else:
                return titles_cache[1]
        else:
            return None


    def get_data(self):
        global titles_cache

        _cache = self.check_cache()
        if _cache:
            return _cache

        tables = self.parse_web()
        rule_search_icon = re.compile(r"src=\"(.*?)\"", re.S)
        rule = re.compile(r"<td>(.*?)</td>", re.S)
        rule_url = re.compile(r"^((https|http)?://)[^\s]+", re.S)
        ret = []
        for table in tables:
            data = rule.findall(table)
            if len(data) != 5:
                continue
            get_url_re = rule_search_icon.findall(data[0])
            if get_url_re:
                if rule_url.findall(get_url_re[0]):
                    url = get_url_re[0]
                    title_jp = data[1].strip()
                    title_cn = data[2].strip()
                    desc_jp = data[3].strip()
                    desc_cn = data[4].strip()
                    ret.append({
                        "icon": url, "title_jp": title_jp, "title_cn": title_cn, "desc_jp": desc_jp, "desc_cn": desc_cn
                    })
        titles_cache[0] = time.time()
        titles_cache[1] = ret
        return ret


    def search(self, name: str):
        rule = re.compile(f".*{name}.*", re.S)
        matches = []
        for i in self.get_data():
            if rule.findall(i["title_cn"]):
                matches.append(i)
            elif rule.findall(i["title_jp"]):
                matches.append(i)
        return matches


if __name__ == "__main__":
    psr = TitleParser()
    print(json.dumps(psr.get_data(), ensure_ascii=False))
