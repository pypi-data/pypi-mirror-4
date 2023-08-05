# package

ROOT_LIST = ('aero','arpa','asia','biz','cat','co','com','coop','edu','gov',
             'int','info','jobs','mil','mobi','museum','name','net','org',
             'pro','tel','travel','xxx')

AREA_LIST = ('ac.ae', 'sch.ae', 'ac.at', 'or.at', 'gv.at', 'priv.at', 'id.au', 'oz.au', 'asn.au', 'csiro.au', 'telememo.au', 'conf.au', 
             'otc.au', 'ac.be', 'belgie.be', 'dns.be', 'fgov.be', 'adm.br', 'adv.br', 'agr.br', 'am.br', 'arq.br', 'art.br', 'ato.br', 
             'bio.br', 'bmd.br', 'cim.br', 'cng.br', 'cnt.br', 'ecn.br', 'eng.br', 'esp.br', 'etc.br', 'eti.br', 'far.br', 'fm.br', 'fnd.br', 
             'fot.br', 'fst.br', 'g12.br', 'ggf.br', 'imb.br', 'ind.br', 'inf.br', 'jor.br', 'lel.br', 'mat.br', 'med.br', 'mus.br', 'nom.br', 
             'not.br', 'ntr.br', 'odo.br', 'ppg.br', 'psc.br', 'psi.br', 'qsl.br', 'rec.br', 'slg.br', 'srv.br', 'tmp.br', 'trd.br', 'tur.br', 
             'tv.br', 'vet.br', 'zlg.br', 'ab.ca', 'bc.ca', 'mb.ca', 'nb.ca', 'nf.ca', 'nl.ca', 'ns.ca', 'nt.ca', 'nu.ca', 'on.ca', 'pe.ca', 
             'qc.ca', 'sk.ca', 'yk.ca', 'gc.ca', 'ac.cn', 'ah.cn', 'bj.cn', 'cq.cn', 'gd.cn', 'gs.cn', 'gx.cn', 'gz.cn', 'hb.cn', 'he.cn', 
             'hi.cn', 'hk.cn', 'hl.cn', 'hn.cn', 'jl.cn', 'js.cn', 'ln.cn', 'mo.cn', 'nm.cn', 'nx.cn', 'qh.cn', 'sc.cn', 'sn.cn', 'sh.cn', 
             'sx.cn', 'tj.cn', 'tw.cn', 'xj.cn', 'xz.cn', 'yn.cn', 'zj.cn', 'arts.co', 'firm.co', 'nom.co', 'rec.co', 'store.co', 'web.co', 
             'ac.cr', 'ed.cr', 'fi.cr', 'go.cr', 'or.cr', 'sa.cr', 'ac.cy', 'art.do', 'gob.do', 'sld.do', 'web.do', 'ass.dz', 'pol.dz', 'art.dz', 
             'k12.ec', 'fin.ec', 'med.ec', 'pri.ee', 'fie.ee', 'med.ee', 'eun.eg', 'sci.eg', 'ind.er', 'gob.es', 'nom.es', 'ac.fj', 'id.fj', 
             'school.fj', 'ac.fk', 'nom.fk', 'asso.fr', 'nom.fr', 'barreau.fr', 'prd.fr', 'presse.fr', 'tm.fr', 'aeroport.fr', 'assedic.fr', 
             'avocat.fr', 'avoues.fr', 'cci.fr', 'chambagri.fr', 'chirurgiens-dentistes.fr', 'experts-comptables.fr', 'geometre-expert.fr', 
             'gouv.fr', 'greta.fr', 'huissier-justice.fr', 'medecin.fr', 'notaires.fr', 'pharmacien.fr', 'port.fr', 'veterinaire.fr', 'pvt.ge', 
             'sch.gg', 'ac.gg', 'ltd.gg', 'ind.gg', 'alderney.gg', 'guernsey.gg', 'sark.gg', 'gob.gt', 'ind.gt', 'idv.hk', '2000.hu', 'erotika.hu', 
             'jogasz.hu', 'sex.hu', 'video.hu', 'agrar.hu', 'film.hu', 'konyvelo.hu', 'shop.hu', 'bolt.hu', 'forum.hu', 'lakas.hu', 'suli.hu', 
             'priv.hu', 'casino.hu', 'games.hu', 'media.hu', 'szex.hu', 'sport.hu', 'city.hu', 'hotel.hu', 'news.hu', 'tozsde.hu', 'tm.hu', 
             'erotica.hu', 'ingatlan.hu', 'reklam.hu', 'utazas.hu', 'ac.id', 'go.id', 'or.id', 'ac.il', 'k12.il', 'muni.il', 'idf.il', 'ac.im', 
             'lkd.co.im', 'nic.im', 'plc.co.im', 'ac.in', 'ernet.in', 'nic.in', 'res.in', 'gen.in', 'firm.in', 'ind.in', 'ac.je', 'ind.je', 
             'jersey.je', 'ltd.je', 'sch.je', 'ad.jp', 'ac.jp', 'go.jp', 'or.jp', 'ne.jp', 'gr.jp', 'ed.jp', 'lg.jp', 'hokkaido.jp', 'aomori.jp', 
             'iwate.jp', 'miyagi.jp', 'akita.jp', 'yamagata.jp', 'fukushima.jp', 'ibaraki.jp', 'tochigi.jp', 'gunma.jp', 'saitama.jp', 'chiba.jp', 
             'tokyo.jp', 'kanagawa.jp', 'niigata.jp', 'toyama.jp', 'ishikawa.jp', 'fukui.jp', 'yamanashi.jp', 'nagano.jp', 'gifu.jp', 'shizuoka.jp', 
             'aichi.jp', 'mie.jp', 'shiga.jp', 'kyoto.jp', 'osaka.jp', 'hyogo.jp', 'nara.jp', 'wakayama.jp', 'tottori.jp', 'shimane.jp', 'okayama.jp', 
             'hiroshima.jp', 'yamaguchi.jp', 'tokushima.jp', 'kagawa.jp', 'ehime.jp', 'kochi.jp', 'fukuoka.jp', 'saga.jp', 'nagasaki.jp', 'kumamoto.jp', 
             'oita.jp', 'miyazaki.jp', 'kagoshima.jp', 'okinawa.jp', 'sapporo.jp', 'sendai.jp', 'yokohama.jp', 'kawasaki.jp', 'nagoya.jp', 'kobe.jp', 
             'kitakyushu.jp', 'utsunomiya.jp', 'kanazawa.jp', 'takamatsu.jp', 'matsuyama.jp', 'per.kh', 'ac.kr', 'go.kr', 'ne.kr', 'or.kr', 'pe.kr', 
             're.kr', 'seoul.kr', 'kyonggi.kr', 'id.lv', 'asn.lv', 'conf.lv', 'press.ma', 'ac.ma', 'tm.mt', 'uu.mt', 'alt.na', 'cul.na', 'unam.na', 
             'telecom.na', 'ac.ng', 'sch.ng', 'gob.ni', 'nom.ni', 'ac.nz', 'cri.nz', 'gen.nz', 'geek.nz', 'iwi.nz', 'maori.nz', 'school.nz', 'ac.om', 
             'mod.om', 'med.om', 'ac.pa', 'gob.pa', 'sld.pa', 'gob.pe', 'nom.pe', 'ac.pg', 'ngo.ph', 'aid.pl', 'agro.pl', 'atm.pl', 'auto.pl', 
             'gmina.pl', 'gsm.pl', 'mail.pl', 'miasta.pl', 'media.pl', 'nieruchomosci.pl', 'nom.pl', 'pc.pl', 'powiat.pl', 'priv.pl', 'realestate.pl', 
             'rel.pl', 'sex.pl', 'shop.pl', 'sklep.pl', 'sos.pl', 'szkola.pl', 'targi.pl', 'tm.pl', 'tourism.pl', 'turystyka.pl', 'fam.pk', 'web.pk', 
             'gob.pk', 'gok.pk', 'gon.pk', 'gop.pk', 'gos.pk', 'plo.ps', 'sec.ps', 'asso.re', 'nom.re', 'tm.ro', 'nt.ro', 'nom.ro', 'rec.ro', 'arts.ro', 
             'firm.ro', 'store.ro', 'www.ro', 'pp.ru', 'sch.sa', 'med.sa', 'pub.sa', 'sch.sd', 'med.sd', 'tm.se', 'press.se', 'parti.se', 'brand.se', 
             'fh.se', 'fhsk.se', 'fhv.se', 'komforb.se', 'kommunalforbund.se', 'komvux.se', 'lanarb.se', 'lanbib.se', 'naturbruksgymn.se', 'sshn.se', 
             'pp.se', 'per.sg', 'saotome.st', 'principe.st', 'consulado.st', 'embaixada.st', 'store.st', 'gob.sv', 'red.sv', 'ac.th', 'go.th', 'or.th', 
             'ens.tn', 'fin.tn', 'nat.tn', 'ind.tn', 'intl.tn', 'rnrt.tn', 'rnu.tn', 'rns.tn', 'tourism.tn', 'bbs.tr', 'k12.tr', 'gen.tr', 'nic.tt', 
             'us.tt', 'uk.tt', 'ca.tt', 'eu.tt', 'es.tt', 'fr.tt', 'it.tt', 'se.tt', 'dk.tt', 'be.tt', 'de.tt', 'at.tt', 'au.tt', 'idv.tw', 'ac.ug', 
             'or.ug', 'go.ug', 'me.uk', 'ltd.uk', 'plc.uk', 'sch.uk', 'nic.uk', 'ac.uk', 'nhs.uk', 'police.uk', 'mod.uk', 'dni.us', 'fed.us', 'gub.uy', 
             'arts.ve', 'bib.ve', 'firm.ve', 'nom.ve', 'rec.ve', 'store.ve', 'tec.ve', 'web.ve', 'ac.vn', 'health.vn', 'de.vu', 'ch.vu', 'fr.vu', 
             'ac.yu', 'ac.za', 'alt.za', 'bourse.za', 'city.za', 'law.za', 'ngo.za', 'nom.za', 'school.za', 'tm.za', 'web.za', 'ac.zw', 'eu.org', 
             'au.com', 'br.com', 'cn.com', 'de.com', 'de.net', 'eu.com', 'gb.com', 'gb.net', 'hu.com', 'no.com', 'qc.com', 'ru.com', 'sa.com', 'se.com', 
             'uk.com', 'uk.net', 'us.com', 'uy.com', 'za.com', 'dk.org', 'fax.nr', 'mob.nr', 'mobil.nr', 'mobile.nr', 'tlf.nr', 'e164.arpa')

def get_host(url):
    tmp = url.split('http://')
    if len(tmp)>1: tmp = tmp[1]
    else: tmp = url
    host = ''
    url = tmp.split('/')[0].split(':')[0].split('%')[0].split('?')[0].split('#')[0]
    if url != 'net.cn':
        host_tmp1 = url.split('.')
        if len(host_tmp1)<=2: return url
        
        ''''host_second' for domain name of the second word，if 'host_second' in the ROOT_LIST，the url's host=A third from bottom of words + the last two words'''
        host_second = host_tmp1[-2]
        set_area = host_tmp1[-2] + '.' + host_tmp1[-1]
        if host_second in ROOT_LIST or set_area in AREA_LIST:
            host = host_tmp1[-3] + '.' + host_tmp1[-2] + '.' + host_tmp1[-1]
        else:
            host = host_tmp1[-2] + '.' + host_tmp1[-1]
    else:
        host = 'net.cn'
    return host

def get_subdomain(url):
    '''
    get the subdomain
    '''
    try:
        tmp = url.split('://')
        if len(tmp)>1: tmp = tmp[1]
        else: tmp = url 
        url = tmp.split('/')[0]
        url = url.split('#')[0]
        url = url.split('?')[0]
        url = url.split('%')[0]
        url = url.split('&')[0]
        url = url.split(':')[0]
    except:
	return None
    url = url.lower()
    return url


