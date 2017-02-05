from mongoengine import *
import time

from . import utils
from . import settings


connect(settings.DATABASE["name"])


class StockHistory(EmbeddedDocument):
    time=FloatField(required=True)
    price=FloatField(required=True)

    def init(self, price):
        self.time = time.time()
        self.price = price


class Stock(Document):
    name=StringField(required=True)
    price=FloatField(required=True)
    history=EmbeddedDocumentListField(StockHistory)
    trend=FloatField()
    blacklisted=BooleanField()

    def buy_one(self):
        if self.blacklisted:
            return False
        self.price += 1
        hist = StockHistory()
        hist.init(self.price)
        self.history.append(hist)
        self.trend = 1.0
        self.blacklisted = False
        self.save()
        return True

    def sell_one(self):
        if self.blacklisted:
            return False
        self.price -= 1
        hist = StockHistory()
        hist.init(self.price)
        self.history.append(hist)
        self.trend = -1.0
        self.save()
        return True

    def get_id(self):
        return str(self.id)

    def get_value(self, amount):
        """Get the current evaluation of a stock"""
        if amount > 0:
            total_worth = (self.price * (self.price + 1)) / 2.0
            other_worth = 0
            if amount < self.price:
                # Others own shares...
                not_my_shares = self.price - amount
                other_worth = (not_my_shares*(not_my_shares+1)) / 2.0
            return total_worth - other_worth
        return 0

    def blacklist(self):
        """
        Flag the meme as blacklisted, and don't show on the main page.
        It will continue to show in a shareholder's portfolio, but they cannot buy or sell.
        """
        self.blacklisted = True
        self.save()


class User(Document):
    fb_id=StringField(required=True, primary_key=True) #Primary 
    holdings=DictField()
    name=StringField(required=True)
    money=FloatField(required=True)
    stock_value=FloatField(required=True)
    api_key=StringField(required=True)
    admin=BooleanField()

    # holdings Example 
    # { 
    #    "stock_id": amount
    # }

    def init(self, name, fb_id):
        self.fb_id = fb_id
        self.name = name
        self.money = settings.INITIAL_MONEY
        self.stock_value = 0
        self.holdings = {}
        self.api_key = utils.get_new_key()
        self.admin = False
        self.save()

    # 
    # API for database updates
    #

    def buy_one(self, stock):
        """
        Step 1: modify the user holdings
        Step 2: modify the market price
        Step 3: modify the user account totals
        """
        if (self.money > stock.price and not stock.blacklisted):
            if str(stock.id) in self.holdings.keys():
                self.holdings[str(stock.id)] += 1
            else:
                self.holdings[str(stock.id)] = 1
            if stock.buy_one():
                self.stock_value += stock.price
                self.money -= stock.price
                self.save()
                return True
        return False

    def sell_one(self, stock):
        """
        Step 1: modify the user holdings
        Step 2: modify the suer account totals
        Step 3: modify the market price
        """
        if str(stock.id) in self.holdings.keys() and not stock.blacklisted:
            if self.holdings[str(stock.id)] >= 1:
                self.money += stock.price
                self.stock_value -= stock.price
                self.holdings[str(stock.id)] -= 1
                if stock.sell_one():
                    self.save()
                    return True
        return False

    def get_holdings(self):
        """
        Process this server-side so the client doesn't have to make n requests to resolve each ID
        """
        ret = [{
                "name": Stock.objects.get(id=key).name, 
                "amount": self.holdings[key],
                "id": key
            } for key in self.holdings.keys()]
        ret = sorted(ret, 
            key=lambda k: k['amount'], 
            reverse=True) 
        return ret

    def get_id(self):
        """
        Given the primary key for User, return an instance of the subclass implementation
        """
        return self.fb_id

    def get_role(self):
        if self.admin:
            return 'admin'
        return 'user'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return self.admin


def sanity_checks():
    # Add Blacklisting
    # stocks = Stock.objects(blacklisted__ne=True)
    # for stock in stocks:
    #     stock.blacklisted = False
    #     stock.save()

    # Add stock_value property
    users = User.objects(stock_value__exists=False)
    for user in users:
        holdings = user.get_holdings()
        user.stock_value = 0.0;
        for item in holdings:
            user.stock_value += Stock.objects.get(id=item['id']).get_value(item['amount'])
        user.save()