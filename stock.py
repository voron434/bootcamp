import itertools
import random


class Merchant():
    strategies = [
        "Альтруист", "Кидала", "Хитрец",
        "Непредсказуемый", "Злопамятный", "Ушлый",
    ]
    merchants_created = 0

    def __init__(self, role=None):
        Merchant.merchants_created += 1
        self.merchant_id = Merchant.merchants_created
        if not role or role not in Merchant.strategies:
            self.role = None
        else:
            self.role = role
        self.journal = {}
        self.money = 0

    def _is_cooperating(self, merchant_id):
        if self.role == "Альтруист":
            decision = True
        elif self.role == "Кидала":
            decision = False
        elif self.role == "Хитрец":
            if merchant_id in self.journal:
                decision = self.journal[merchant_id]["his_last_turn"]
            else:
                decision = True
        elif self.role == "Непредсказуемый":
            decision = bool(random.getrandbits(1))
        elif self.role == "Злопамятный":
            if merchant_id in self.journal and self.journal[merchant_id]["is_treated_me"]:
                decision = False
            else:
                decision = True
        elif self.role == "Ушлый":
            if merchant_id not in self.journal:
                decision = True
            elif self.journal[merchant_id]["turns_played"] in [0, 2, 3]:
                decision = True
            elif self.journal[merchant_id]["turns_played"] == 1:
                decision = False
            elif self.journal[merchant_id]["is_treated_me"]:
                decision = False
            else:
                if merchant_id in self.journal:
                    decision = self.journal[merchant_id]["his_last_turn"]
                else:
                    decision = True
        else:
            raise ValueError("Role should be one of expected types.")
        is_mistaken = not bool(random.randrange(0, 21))
        if is_mistaken:
            return not decision
        else:
            return decision

    def _make_journal_record(self, merchant_id, decision):
        if merchant_id not in self.journal:
            self.journal[merchant_id] = {
                "is_treated_me": not decision,
                "his_last_turn": decision,
                "turns_played": 1,
            }
        else:
            self.journal[merchant_id]["his_last_turn"] = decision
            self.journal[merchant_id]["turns_played"] += 1
            if not self.journal[merchant_id]["is_treated_me"] and not decision:
                self.journal[merchant_id]["is_treated_me"] = True


class Stock():

    def __init__(self, merchants=[]):
        self.year = 0
        self.merchants = merchants
        self.is_smb_won = False

    def tick_year(self):
        for first_merchant, second_merchant in itertools.combinations(self.merchants, 2):
            for _ in range(random.randrange(5, 11)):
                self._trade(first_merchant, second_merchant)
        self.year += 1
        self._end_of_year()

    def _end_of_year(self):
        merchants_rating = sorted(
            self.merchants,
            key=lambda merchant: merchant.money,
            reverse=True
        )
        top_roles = [merchant.role for merchant in merchants_rating[:12]]
        newbies = [Merchant(role) for role in top_roles]
        new_merchants_list = merchants_rating[:48] + newbies
        self.merchants = new_merchants_list
        for merchant in self.merchants:
            merchant.money = 0
            if merchant.journal:
                merchant.journal["turns_played"] = 0
        roles = [merchant.role for merchant in self.merchants]
        if roles.count(self.merchants[0].role) == 60:
            self.is_smb_won = True

    def _trade(self, first_merchant, second_merchant):
        decision_first = first_merchant._is_cooperating(second_merchant.merchant_id)
        decision_second = second_merchant._is_cooperating(first_merchant.merchant_id)
        if decision_first:
            if decision_second:
                first_merchant.money += 4
                second_merchant.money += 4
            else:
                first_merchant.money += 1
                second_merchant.money += 5
        else:
            if decision_second:
                first_merchant.money += 5
                second_merchant.money += 1
            else:
                first_merchant.money += 2
                second_merchant.money += 2
        first_merchant._make_journal_record(second_merchant.merchant_id, decision_second)
        second_merchant._make_journal_record(first_merchant.merchant_id, decision_first)


if __name__ == "__main__":
    merchants = []
    for strategy in Merchant.strategies:
        merchants += [Merchant(strategy) for _ in range(10)]
    stock = Stock(merchants)
    while not stock.is_smb_won:
        stock.tick_year()
    print("Выиграл {0} за {1} лет".format(stock.merchants[0].role, stock.year))
