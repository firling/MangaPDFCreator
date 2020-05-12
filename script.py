import requests, codecs, base64, os, img2pdf
from bs4 import BeautifulSoup

def extention(urlImage, name, chapter, page):
    url = urlImage.format(name.replace(" ", "-").lower(), chapter, page)

    for ext in ["png", "jpg", "jpeg"]:
        res = requests.get(url + ext, stream=True)
        if res.status_code != 200:
            pass
        else:
            return ext

    return False


name = "naruto"
chapter = 1

urlStarts = ["https://www.scan-vf.net/{}/chapitre-{}",
             "https://www.lelscan-vf.com/manga/{}/{}",
             "https://www.lelscan-vf.com/manga/{}/{}"]
urlImagess = ["https://www.scan-vf.net/uploads/manga/{}/chapters/chapitre-{}/{:0>2d}.",
              "https://www.lelscan-vf.com/uploads/manga/{}/chapters/{}vf/{:0>3d}.",
              "https://www.lelscan-vf.com/uploads/manga/{}/chapters/{}/{:0>2d}."]

for i in range(len(urlStarts)):
    urlStart = urlStarts[i]
    urlImages = urlImagess[i]
    ext = extention(urlImages, name, chapter, 1)
    if not ext:
        continue
    else:
        urlImages = urlImages + extention(urlImages, name, chapter, 1)
        break

if not ext:
    urlStart = "https://scan-fr.co/manga/{}/{}"

res = requests.get(urlStart.format(name.replace(" ", "-").lower(), chapter), stream=True)
soup = BeautifulSoup(res.text, "lxml")

if not ext:
    url = soup.find("img", {"class": "scan-page"})["src"][1:-1]
    url = url.replace(" ", "%20")
    chap = url.find(str(chapter))
    page = url.rfind("1")
    pageSlash = url.rfind("/")
    pagePart = url[pageSlash - len(url) + 1:]
    pagePartNew = pagePart[:pagePart.find(".")]
    chapPart = url[:pageSlash - len(url)]
    chapSlash = chapPart.rfind("/")
    chapPart = chapPart[chapSlash - len(chapPart) + 1:]
    urlImages = url.replace(pagePart, "{}" + pagePart[pagePart.find("."):]).replace(chapPart, "{}")

select = soup.find("select", {'id': "page-list"})
for i in range(len(select.findAll("option"))):
    url = urlImages
    if not ext:
        urlRequest = url.format(chapPart, pagePartNew)
        pagePartOld = pagePartNew
        pagePartNew = pagePartNew.replace(str(i+1), str(i+2))
        if pagePartNew == pagePartOld:
            pagePartNew = pagePartNew[:len(pagePartNew)-1] + str(int(pagePartNew[len(pagePartNew)-1:]) + 2)
        while len(pagePartNew) > len(pagePartOld):
            pagePartNew = pagePartNew[1:]
    else:
        urlRequest = url.format(name.replace(" ", "-").lower(), chapter, i+1)
    res = requests.get(urlRequest, stream=True)
    if res.status_code != 200:
        continue

    hex = codecs.encode(res.content, "hex").decode("ascii")
    b64 = codecs.encode(codecs.decode(hex, 'hex'), 'base64').decode()

    before = "0" if len(str(i+1)) == 1 else ""
    with open("./img/img{}.png".format(before + str(i+1)), "wb") as f:
        f.write(base64.decodebytes(bytes(b64, 'utf-8')))
        f.close()

with open(name.replace(" ", "-") + str(chapter) + ".pdf", "wb") as fh:
    fh.write(img2pdf.convert(["./img/" + i for i in os.listdir('./img')]))

for i in os.listdir('./img'):
    os.remove("./img/" + i)
