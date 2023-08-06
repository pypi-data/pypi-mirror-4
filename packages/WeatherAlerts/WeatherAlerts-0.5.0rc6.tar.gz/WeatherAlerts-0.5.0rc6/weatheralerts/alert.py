

class Alert():
    '''
    Create an alert object with the cap dict created from cap xml parser.

    This object won't be pretty... it's mostly a bunch of property methods to
    sanitize and muck around with the raw cap data. Using individual properties
    and methods instead of a special getattr so that we can more easily standardize
    the Alert API. This may be revisted in the future as the project becomes more
    stable.


    '''
    def __init__(self, cap_dict):
        self._raw = cap_dict

    def _ts_parse(self, ts):
        #FIXME: should return datetime
        dt = ts
        return dt

    @property
    def title(self):
        '''Alert title'''
        return self._raw['title']

    @property
    def summary(self):
        '''Alert summary'''
        return self._raw['summary']

    @property
    def areadesc(self):
        '''A more generic area description'''
        return self._raw['cap:areaDesc']

    @property
    def event(self):
        '''alert event type'''
        return self._raw['cap:event']

    @property
    def samecodes(self):
        '''samecodes for the alert area'''
        return self._raw['samecodes']

    @property
    def zonecodes(self):
        '''UCG codes for the alert area (these are sometimes referred to as county codes,
        but that's not quite accurate)'''
        try:
            return self._raw['UCG']
        except Exception:
            return []

    @property
    def expiration(self):
        '''Expiration of the alert (datetime object)'''
        ts = self._ts_parse(self._raw['cap:expires'])
        return ts

    @property
    def updated(self):
        '''Last update to the alert (datetime object)'''
        ts = self._ts_parse(self._raw['updated'])
        return ts

    @property
    def effective(self):
        '''Effective timestamp of the alert (datetime object)'''
        ts = self._ts_parse(self._raw['cap:effective'])
        return ts

    @property
    def published(self):
        '''Published timestamp of the alert (datetime object)'''
        ts = self._ts_parse(self._raw['published'])
        return ts

    @property
    def severity(self):
        '''Severity of alert i.e. minor, major, etc'''
        return self._raw['cap:severity']

    @property
    def category(self):
        '''Category of alert i.e. Met, Civil, etc'''
        return self._raw['cap:category']

    @property
    def urgency(self):
        '''Alert urgency'''
        return self._raw['cap:urgency']
