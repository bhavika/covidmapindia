import bs4
import requests
import pandas as pd

page_iterator_url = (
    "https://www.divcommpunecovid.com/ccsbeddashboard/hsr?d-3677810-p={}"
)


def get_table_data(table):
    def rowgetDataText(tr, coltag="td"):  # td (data) or th (header)
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]

    rows = []
    trs = table.find_all("tr")
    headerow = rowgetDataText(trs[0], "th")
    if headerow:  # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs:
        rows.append(rowgetDataText(tr, "td"))
    return rows


def scrape_page(page):
    url = page_iterator_url.format(page)
    page_source = requests.get(url).text
    soup = bs4.BeautifulSoup(page_source, "html.parser")
    page = soup.find("div", {"class": "content2 tableFixHead"})
    table = page.find("table", {"id": "tablegrid"})
    data = get_table_data(table)
    data_df = pd.DataFrame(data)

    # assign column names
    cols = data_df.iloc[0]
    data_df.columns = cols
    return data_df


def build_dataset():
    page_dfs = []
    columns = None

    for page in range(1, 6):
        df = scrape_page(page)
        if columns is None:
            columns = list(df.columns.values)
        page_dfs.append(df[1:])

    data_df = pd.concat(page_dfs, axis=0)
    data_df.to_csv("data/pune_beds.csv", header=columns)


if __name__ == "__main__":
    build_dataset()
