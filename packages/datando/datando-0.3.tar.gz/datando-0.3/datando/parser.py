import datando.gregorian
import datando.julian
import datando.kernel
import datando.jd
import datando.mjd
import datando.rjd
import datando.tjd
import datando.djd
import datando.jd

registered_classes = [datando.gregorian.GregorianDateTime,
                      datando.julian.JulianDateTime,
                      datando.jd.JDDateTime,
                      datando.mjd.MJDDateTime,
                      datando.rjd.RJDDateTime,
                      datando.tjd.TJDDateTime,
                      datando.djd.DJDDateTime,
                      datando.kernel.LPInterval]

def parse(date_str):
    for c in registered_classes:
        if date_str.startswith(c.get_prefix()):
            return c.parse(date_str)
    return datando.kernel.LPDateTime.parse(date_str)
