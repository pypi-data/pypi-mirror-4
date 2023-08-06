import pyregion

import pyfits

# At some point, pyfits.Card.fromstring has changed from unbound
# method to bounded method.

if pyfits.Card.fromstring.__self__: # 
    def pyfits_card_fromstring(l):
        return pyfits.Card.fromstring(l)
else:
    def pyfits_card_fromstring(l):
        c = pyfits.Card()
        return c.fromstring(l)

def demo_header():
    cards = pyfits.CardList()
    for l in open("sample_fits01.header"):
        card = pyfits_card_fromstring(l.strip())
        cards.append(card)
    h = pyfits.Header(cards)
    return h



if 1:

    region_list = ["test01_fk5_sexagecimal.reg",
                   "test01_gal.reg",
                   "test01_img.reg",
                   "test01_ds9_physical.reg",
                   "test01_fk5_degree.reg",
                   "test01_mixed.reg",
                   "test01_ciao.reg",
                   "test01_ciao_physical.reg",
                   ]

    h = demo_header()
    
    for region_file in region_list[1:2]:
        reg = pyregion.open(region_file)
        reg01 = reg.as_imagecoord(h)
