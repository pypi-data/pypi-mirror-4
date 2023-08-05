def percent(self, numerator, denominator):
    if denominator == 0:
        return "infinity"
    return "%.4g%%" % (float(numerator)/float(denominator) * 100)
