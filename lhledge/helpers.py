import pycountry as pc

def alpha3_to_alpha2(cc3):
    try:
        country = pc.countries.get(alpha_3=cc3)
        return country.alpha_2
    except:
        return "??"
