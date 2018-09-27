def xdaili(self):
    nn_url = "http://www.xdaili.cn/freeproxy.html"
    try:
        r = requests.get(nn_url, headers=self.header, timeout=30)
        r.encoding = 'utf-8'
        html = r.text
        tree = etree.HTML(html)
        raw_tables = tree.xpath('//table')
        tables = raw_tables[:4]
        for table in tables:
            trs = table.xpath('./tr')
            trss = trs[1:]
            for tr in trss:
                tds = tr.xpath("./td/text()")
                ipport = str(tds[4] + "://" + tds[0] + ":" + tds[1]).lower()
                raw_ips.append(ipport)
        print("ipyqle")
    except:
        print("cannot open" + "ipyqle")