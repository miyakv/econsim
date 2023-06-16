from accountant import Accountant
from market import *
from new_exceptions import *
import messages


class Game:
    def __init__(self):
        self.finished = False
        print(messages.init.welcome)
        self.acc = Accountant('ex.acc', 'Player', 5, ['rub', 'usd'])
        self.markets = [Market('rub', 'usd', self.acc, 'usdrub.market')]
        self.logged_idn = None
        self.main_cycle()

    def logged_in(self):
        if not self.acc.account_exists(self.logged_idn):
            return False
        return True

    def restart(self):
        if input(messages.restart.warning).lower() != 'y':
            print(messages.restart.aborted)
            return
        self.acc = Accountant('ex.acc', 'Player', 5, ['rub', 'usd'], allow_existing=False)
        self.markets = [Market('rub', 'usd', self.acc, 'usdrub.market', allow_existing=False)]

    def create_account(self):
        success = False
        name = None
        while not success:
            name = input(messages.create.name_input)
            if name.strip() == '':
                print(messages.create.empty_name)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return
            else:
                success = True
        print(messages.create.success.format(name, self.acc.create_account(name)))

    def delete_account(self):
        success = False
        idn = None
        while not success:
            idntext = input(messages.delete.id_input)
            try:
                idn = int(idntext)
            except ValueError:
                print(messages.misc.id_int_error)
                if input(messages.misc.ask_continue) != 'y':
                    return
            else:
                success = True
        try:
            self.acc.delete_account(idn)
        except IdNotFoundError as e:
            print(e)
        else:
            print(messages.delete.success.format(idn))
        if not self.logged_in():
            print(messages.login.required)


    @staticmethod
    def get_number(message, allow_negative=False, allow_zero=False):
        success = False
        while not success:
            try:
                amount = float(input(message))
            except ValueError:
                print(messages.amount.float_error)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return False
            if amount < 0 and not allow_negative:
                print(messages.amount.negative_error)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return False
            elif amount == 0 and not allow_zero:
                print(messages.amount.zero_error)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return False
            else:
                success = True
        return amount

    def get_currency(self, message=messages.transfer.currency_input):
        success = False
        while not success:
            currency = input(message.format(', '.join(self.acc.currencies_list))).lower()
            if currency not in self.acc.currencies_list:
                print(messages.transfer.currency_not_exist.format(currency))
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return False
            else:
                success = True
        return currency

    def transfer(self):
        success = False
        while not success:
            try:
                from_id = int(input(messages.transfer.from_input))
                to_id = int(input(messages.transfer.to_input))
            except ValueError:
                print(messages.misc.id_int_error)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return
            else:
                if self.acc.account_exists(from_id) and self.acc.account_exists(to_id):
                    currency = self.get_currency()
                    if not currency:
                        return
                    amount = self.get_number(message=messages.transfer.amount, allow_negative=True)
                    if not amount:
                        return
                    success = True
                else:
                    print(messages.misc.id_not_exists)
                    if input(messages.misc.ask_continue.lower()) != 'y':
                        return
        try:
            self.acc.transfer(from_id, to_id, currency, amount)
        except NotEnoughMoney as e:
            print(e)
        else:
            print(messages.transfer.success.format(amount, currency, from_id, to_id))

    def give_all(self):
        currency = self.get_currency()
        if not currency:
            return
        amount = self.get_number(message=messages.transfer.amount, allow_negative=True)
        if not amount:
            return
        try:
            self.acc.give_all(currency, amount)
        except NotEnoughMoney as e:
            print(e)
        except IdNotFoundError as e:
            print(e)
        else:
            print(messages.transfer.success.format(amount, currency, 'banker', 'all'))

    def give(self):
        success = False
        to_all = False
        while not success:
            to_id = input(messages.transfer.to_input)
            try:
                to_id = int(to_id)
            except ValueError:
                if to_id == '@':
                    to_all = True

                else:
                    print(messages.misc.id_int_error)
                    if input(messages.misc.ask_continue.lower()) != 'y':
                        return
            currency = self.get_currency()
            if not currency:
                return
            try:
                amount = float(input(messages.transfer.amount))
            except ValueError:
                print(messages.amount.float_error)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return
            else:
                success = True
        if to_all:
            self.give_all(currency, amount)
            return
        try:
            self.acc.give(to_id, currency, amount)
        except NotEnoughMoney as e:
            print(e)
        except IdNotFoundError as e:
            print(e)
        else:
            print(messages.transfer.success.format(amount, currency, 'banker', to_id))

    def order(self):
        if not self.acc.account_exists(self.logged_idn):
            print(messages.misc.id_not_exists)
            return
        trader_idn = self.logged_idn
        # Choosing currencies to sell and to buy
        to_buy = self.get_currency(messages.market.to_buy)
        if not to_buy:
            return
        to_sell = self.get_currency(messages.market.to_sell)
        if not to_sell:
            return

        # Choosing market where the currencies are traded
        m = None
        for market in self.markets:
            if market.currency_a in (to_buy, to_sell) and market.currency_b in (to_buy, to_sell):
                m = market
        if m is None:
            print(messages.market.pair_does_not_exist)
            return

        # selecting whether the order will be market or limit
        success = False
        while not success:
            try:
                order_type = int(input(messages.market.order_type))
            except ValueError:
                print(messages.market.type_error)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return
            else:
                if order_type in (1, 2):
                    success = True
                else:
                    print(messages.market.type_error)
                    if input(messages.misc.ask_continue.lower()) != 'y':
                        return

        # selecting amount
        c = m.currency_b
        print(messages.market.lot_info.format(c, m.lot_size))
        if to_buy == c:
            amount = self.get_number(messages.market.amount.format(c, 'buy'))
            if not amount:
                return
            amount = amount // m.lot_size * m.lot_size
        elif to_sell == c:
            amount = self.get_number(messages.market.amount.format(c, 'sell'))
            if not amount:
                return
            amount = amount // m.lot_size * m.lot_size

        if order_type == 1:
            success = False
            while not success:
                price = self.get_number(messages.market.price.format(m.currency_a, m.currency_b))
                try:
                    if to_buy == c:
                        m.place_limit_order(trader_idn, price, amount, 'buy')
                    elif to_sell == c:
                        m.place_limit_order(trader_idn, price, amount, 'sell')
                except Exception as e:
                    print(e)
                    if input(messages.misc.ask_continue.lower()) != 'y':
                        return
                else:
                    success = True
                    if to_buy == c:
                        print(messages.market.limit_success.format('buy', amount, c, price, to_sell, c))
                    if to_sell == c:
                        print(messages.market.limit_success.format('sell', amount, c, price, to_buy, c))

        if order_type == 2:
            try:
                if to_buy == c:
                    a = m.place_market_order(trader_idn, amount, 'buy')
                elif to_sell == c:
                    a = m.place_market_order(trader_idn, amount, 'sell')
            except Exception as e:
                print(e)
                if input(messages.misc.ask_continue.lower()) != 'y':
                    return
            else:
                if to_buy == c:
                    print(messages.market.market_success.format('bought', amount, c, a, m.currency_a, a / amount, m.currency_a, c))
                if to_sell == c:
                    print(messages.market.market_success.format('sold', amount, c, a, m.currency_a, a / amount, m.currency_a, c))

    def finish(self):
        if input(messages.finish.warning).lower() == 'y':
            self.finished = True

    @staticmethod
    def help():
        print(messages.help.message)

    def login(self):
        success = False
        while not success:
            try:
                idn = int(input(messages.login.id))
            except ValueError:
                print(messages.misc.id_int_error)
                if input(messages.misc.ask_continue).lower() != 'y':
                    return
            else:
                if not self.acc.account_exists(idn):
                    print(messages.misc.id_not_exists)
                    return
                success = True

        self.logged_idn = idn

    def show_markets(self):
        for market in self.markets:
            print(market)

    def show_orders(self):
        if not self.logged_in():
            return
        ids = []
        market_id = 0
        print(messages.market.all_orders.format(self.logged_idn))
        for market in self.markets:
            print(f' = Market {market_id} - {market.currency_b} to {market.currency_a} =')
            ids.append([])
            for order in market.show_orders(self.logged_idn):
                ids[market_id].append(order.idn)
                print(order)
            market_id += 1
        return ids

    def cancel_order(self):
        if not self.acc.account_exists(self.logged_in):
            print(messages.misc.id_not_exists)
            return
        ids = self.show_orders()
        try:
            market_id_delete = int(input(messages.market.select))
        except ValueError:
            print(messages.misc.id_int_error)
            return
        if market_id_delete < 0 or market_id_delete >= len(ids):
            print(messages.misc.id_not_exists)

        try:
            order_id_delete = int(input(messages.market.select_cancel_order))
        except ValueError:
            print(messages.misc.id_int_error)
            return
        if order_id_delete not in ids[market_id_delete]:
            print(messages.misc.id_not_exists)

        self.markets[market_id_delete].cancel_order(order_id_delete)

    def create_currency(self):
        name = input(messages.create_currency.create).lower()
        if name in self.acc.currencies_list:
            print(messages.create_currency.already_exists)
            return
        if name == '':
            print(messages.misc.empty_name)
            return
        c = self.acc.currencies_list[:]
        print(c)
        self.acc.create_currency(name)
        print(c)
        for currency in c:
            self.markets.append(Market(currency, name, self.acc, f'{currency}{name}.market'))

    def main_cycle(self):
        functions = {'restart': self.restart,
                     'addacc': self.create_account,
                     'create': self.create_currency,
                     'delete': self.delete_account,
                     'finish': self.finish,
                     'transfer': self.transfer,
                     'give': self.give,
                     'giveall': self.give_all,
                     'help': self.help,
                     'login': self.login,
                     'order': self.order,
                     'market': self.show_markets,
                     'myorders': self.show_orders,
                     'cancel': self.cancel_order}

        command = input("Input command: ")
        # show acc
        # input command
        # command result
        # input command
        while not self.finished:
            print(self.acc)
            if command.lower() not in functions.keys():
                print(messages.misc.command_not_found.format(command.lower()))
            else:
                functions[command.lower()]()
            command = input("Input command: ")
            os.system('cls')


Game()
