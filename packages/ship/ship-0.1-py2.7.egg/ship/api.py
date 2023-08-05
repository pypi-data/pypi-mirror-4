from itertools import chain

from sqlalchemy import func, desc

from ship.db.config import session
from ship.db.models import Premium, Insurer, Town

def unpack(result):
    return list(chain.from_iterable(result))

def available_years():
    """ Returns the years available in the database. Not to be confused
    with ship.db.load.available_years which resturns the years available
    as rawdata files. 

    The years are returned in descending order.

    """

    # check the smallest table as all table should contain data for
    # each possible year
    query = session.query(Insurer.year).distinct()
    query = query.order_by(desc(Insurer.year))
    
    return unpack(query.all())

def latest_year():
    """ Returns the most current year. """
    years = available_years()
    return years and years[0] or None

def age_group(age):
    """ Returns the age group of the given age. Done static for now as it
    doesn't seem to be changing any time soon.
    """
    assert age >= 0

    if age >= 26: return 26
    if age >= 19: return 19

    return 0

def insurance_types(year=None):
    """ Returns the possible insurance types by year, with the latest 
    year as default. """
    
    year = year or latest_year()
    assert year

    query = session.query(Premium.insurance_type)
    query = query.filter(Premium.year == year)
    query = query.distinct()
    query = query.order_by(Premium.insurance_type)

    return unpack(query.all())

def insurers(year=None):
    """ Returns the insurers of the given or the latest year. """

    year = year or latest_year()
    assert year

    return session.query(Insurer)

def franchises(age=None, year=None):
    """ Returns a list of possible franchises for the given or the latest year. 
    Since kids may have different franchises than adults the list is further
    reduced if the age in question is passed.

    """

    year = year or latest_year()
    assert year

    query = session.query(Premium.franchise)
    query = query.filter(Premium.year == year)

    if age:
        query = query.filter(Premium.age_group == age_group(age))

    query = query.distinct().order_by(Premium.franchise)

    return unpack(query.all())

class Towns(object):

    def __init__(self, query=None):
        self.q = query or session.query(Town)

    def for_year(self, year):
        return Towns(self.q.filter(Town.year==year))

    def with_zipcode(self, zipcode):
        return Towns(self.q.filter(Town.zipcode==zipcode))

    def in_canton(self, canton):
        return Towns(self.q.filter(Town.canton==canton.upper()))

    def regions(self):
        return unpack(self.q.with_entities(Town.region).distinct().all())

class Premiums(object):

    def __init__(self, query=None):
        self.q = query or session.query(Premium)

    def results(self):
        return self.q.order_by(Premium.premium)

    def count(self):
        return self.q.count()

    def for_year(self, year):
        return Premiums(self.q.filter(Premium.year==year))

    def for_swiss(self):
        return Premiums(self.q.filter(Premium.group=='CH'))

    def for_swiss_expats(self):
        return Premiums(self.q.filter(Premium.group=='EU'))

    def for_age(self, age):
        return Premiums(self.q.filter(Premium.age_group==age_group(age)))

    def for_country(self, country):
        return Premiums(self.q.filter(Premium.country==country))

    def for_canton(self, canton):
        return Premiums(self.q.filter(Premium.canton==canton.upper()))

    def for_region(self, region):
        return Premiums(self.q.filter(Premium.region==region))

    def for_town(self, town):
        return self.for_canton(town.canton).for_region(town.region)

    def for_franchises(self, franchises):
        return Premiums(self.q.filter(Premium.franchise.in_(franchises)))

    def for_insurance_types(self, insurance_types):
        return Premiums(self.q.filter(Premium.insurance_type.in_(insurance_types)))

    def with_accident(self):
        return Premiums(self.q.filter(Premium.with_accident==True))

    def for_number_of_kids(self, kids):
        keys = map(lambda n: "K%i" % n, range(1, kids+1))
        return Premiums(self.q.filter(Premium.insurance_type._in(keys)))

    def for_kid(self, kid):
        return Premiums(self.q.filter(Premium.insurance_type == 'K%i' % kid))

    def without_accident(self):
        return Premiums(self.q.filter(Premium.with_accident==False))