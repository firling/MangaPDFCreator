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


name = input("nom du manga: ")
chapterStart = int(input("numéro du premier chapitre que tu veux: "))
chapterEnd = int(input("numéro du dernier chapitre que tu veux (met le meme numéro que le premier chapitre si tu en veux qu'un): "))

print("L'opération peut prendre quelques minutes (surtout si tu veux bcp de pdf).")

urlStarts = ["https://www.lelscan-vf.com/manga/{}/{}",
             "https://www.lelscan-vf.com/manga/{}/{}",
             "https://www.lelscan-vf.com/manga/{}/{}"]
urlImagess = ["https://www.lelscan-vf.com/uploads/manga/{}/chapters/{}vf/{:0>3d}.",
              "https://www.lelscan-vf.com/uploads/manga/{}/chapters/{}/{:0>2d}.",
              "https://www.lelscan-vf.com/uploads/manga/{}/chapters/{}/{:0>3d}."]
for chapter in range(chapterStart, chapterEnd+1):

    for i in range(len(urlStarts)):
        urlStart = urlStarts[i]
        urlImages = urlImagess[i]
        ext = extention(urlImages, name, chapter, 4)
        if not ext:
            continue
        else:
            urlImages = urlImages + ext
            break

    if not ext:
        urlStarts = ["https://www.lelscan-vf.com/manga/{}/{}", "https://scan-fr.co/manga/{}/{}"]
        for urlStart in urlStarts:
            wolapage = 3
            res = requests.get(urlStart.format(name.replace(" ", "-").lower(), chapter) + "/4", stream=True)
            while res.status_code != 200 and wolapage >= 1:
                res = requests.get(urlStart.format(name.replace(" ", "-").lower(), chapter) + "/{}".format(wolapage), stream=True)
                wolapage-=1
            if res.status_code != 200:
                continue
            soup = BeautifulSoup(res.text, "lxml")

            if not ext:
                url = soup.find("img", {"class": "scan-page"})["src"][1:-1]
                url = url.replace(" ", "%20")
                chap = url.find(str(chapter))
                page = url.rfind("1")
                pageSlash = url.rfind("/")
                pagePart = url[pageSlash - len(url) + 1:]
                pagePartNew = pagePart[:pagePart.find(".")]
                pagePartNew = pagePartNew.replace("4", "1")
                chapPart = url[:pageSlash - len(url)]
                chapSlash = chapPart.rfind("/")
                chapPart = chapPart[chapSlash - len(chapPart) + 1:]
                urlImages = url.replace(pagePart, "{}" + pagePart[pagePart.find("."):]).replace(chapPart, "{}")
                test = requests.get(urlImages.format(chapPart, pagePartNew))
                if res.status_code == 200:
                    break
    else:
        res = requests.get(urlStart.format(name.replace(" ", "-").lower(), chapter), stream=True)
        soup = BeautifulSoup(res.text, "lxml")
    try:
        select = soup.find("select", {'id': "page-list"})
    except:
        input("Le manga n'a pas été trouvé....")
        exit(404)
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

    with open("./pdfs/" + name.replace(" ", "-") + str(chapter) + ".pdf", "wb") as fh:
        fh.write(img2pdf.convert(["./img/" + i for i in os.listdir('./img')]))

    for i in os.listdir('./img'):
        os.remove("./img/" + i)

print("wola regarde dans le fichier PDFS ya ce que tu veux")
input("apuis sur une touche pour continuer...")
