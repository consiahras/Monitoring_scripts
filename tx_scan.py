import urllib.request,urllib.parse, urllib.error
from bs4  import BeautifulSoup
import ssl

#Ignore SSL certificate errors
ctx=ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


url='https://www.taxidromikoskodikas.gr/'
#url='https://www.taxidromikoskodikas.gr/nomos/ZAKYNTHOY/perioxi/VOLIMES'
html = urllib.request.urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')



tags = soup('a')
substring="perioxi"
for tag in tags:
    tagstring= tag.get('href', None)
    if tagstring.startswith("/nomos/") and substring not in tagstring:
        print("PERIOXI: ", tagstring)
        url2=("https://www.taxidromikoskodikas.gr/" + tagstring)
        html2=urllib.request.urlopen(url2, context=ctx).read()
        soup2= BeautifulSoup(html2, 'html.parser')
        tags2 = soup2('a')
        for tag2 in tags2:
            tag2string=tag2.get('href', None)
            if tag2string.startswith("/nomos/") and substring in tag2string:
                print(tag2string)
                url3 = ("https://www.taxidromikoskodikas.gr/" + tag2string)
                html3 = urllib.request.urlopen(url3, context=ctx).read()
                soup3 = BeautifulSoup(html3, 'html.parser')
                #Find the table element
                table = soup3.find("table", id="data1")
                #Extract and format the table data
                if table:
                    rows = table.find_all("tr")
                    for row in rows:
                        cells = row.find_all("td")
                        if cells:
                            row_data = [cell.get_text(strip=True) for cell in cells]
                            print("\t".join(row_data))
                else:
                    print("Table not found for url:", url3)
