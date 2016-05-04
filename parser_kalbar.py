import urllib
from bs4 import BeautifulSoup
import pandas as pd

#get master list
master = urllib.urlopen("http://sekolah.data.kemdikbud.go.id/index.php/cpetasebaran/index/000000/")
mastersoup = BeautifulSoup(master)
list_daerah=[]
for opt in mastersoup.find_all('option'):
    daerah={}
    sc_code = opt.get('value')
    if sc_code:
        daerah["code"]=sc_code
        daerah["name"]=''.join(opt.findAll(text=True))
        list_daerah.append(daerah)
list_daerah = list_daerah[:-8]

#lazy_ass
dict_daerah={}
for i in list_daerah:
    dict_daerah[i["code"]]=i["name"][6:]

codelist = [item['code'] for item in list_daerah]

#main loop
dflist = []
for code in codelist:
	print("parsing for code: "+code)
	URL = "http://sekolah.data.kemdikbud.go.id/index.php/cpetasebaran/index/130000/SD"
	f = urllib.urlopen(URL) 
	soup = BeautifulSoup(f)
	if soup.title.string != "Database Error":
		sc = soup.find_all('script')[21].string
		sc_c = sc.strip(' \t\n\r').split(";")
		sc_arr = []
		for s in sc_c:
			sc_arr.append(s.strip(' \t\n\r'))
		sc_name=[]
		sc_latlong=[]
		for line in sc_arr:
			school={}
			if "NPSN" in line:
				#url
				urlsekolah = line.split("=")[7][25:61]
				school["url"] = urlsekolah
				#NPSN
				school["npsn"]= line.split("=")[5][36:44]
				#nama
				sc_str = line.split("=")[8]
				school["name"] = sc_str[9:sc_str.find("</a")]

				#urldetail
				url_detail = "http://sekolah.data.kemdikbud.go.id/index.php/chome/profil/"+urlsekolah
				sekolah = urllib.urlopen(url_detail)
				sekolahsoup = BeautifulSoup(sekolah)
				info = {}
				for a in mastersoup.find_all("div", class_="col-xs-12 col-md-3 text-left"):
					for b in a.text.splitlines(): 
						s =  b.strip().replace(" ", "")
						if s != "":
						#print count
							t = " ".join(s.split()).replace(" ", "").split(":")
							for (k,v) in zip(t[0:][::2],t[1:][::2]):
								info[k]=v
				for keys in info.keys():
					school[keys]=info[keys]
				print school["name"]
				sc_name.append(school)
			if "latLng" in line:
				latlng = line.split("ng(")[1][0:20].split(",")
				school["lat"] = latlng[0]
				school["long"] = latlng[1]
				sc_latlong.append(school)

		#merge two dict list
		for n, l in zip(sc_name,sc_latlong):
			n.update(l)
		d = pd.DataFrame.from_dict(sc_name)
		d['level'] = "SD"
		d['code'] = code
		d['region'] = dict_daerah[code]
		dflist.append(d)
df_national = pd.concat(dflist)
#FILENAME = code+".csv"
df_national.to_csv("kalbar.csv",encoding='utf-8')



