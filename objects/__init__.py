from datetime import date
from datetime import date
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable

from CONFIG import plan_information


class Person:

    def __init__(self, salary: float, name: str):
        self.salary = salary
        self.name = name


class Debt:

    def __init__(self, debt: float, graduation_year: int, person: Person, plan_type: str) -> object:

        # Fixed attributes
        self.start_date = date.today() + relativedelta(months=1) + relativedelta(day=1)
        self.expiry_date = date(graduation_year + 31, 4, 1)
        self.person = person
        self.interest = plan_information[plan_type]['interest_rate']
        self.threshold = plan_information[plan_type]['threshold']
        self.repayment_rate = plan_information[plan_type]['repayment_rate']
        self.plan_type = plan_type
        self.original_debt = debt

        # Changing attributes
        self.debt = debt
        self.current_date = self.start_date
        self.minimum_repayment = self.calculate_minimum_repayment()

        # Metrics to track
        self.interest_accumulated = 0
        self.minimum_repayments_made = 0
        self.overpayments_made = 0
        self.paid = False

    def calculate_minimum_repayment(self):
        monthly_taxable_income = (self.person.salary - self.threshold) / 12
        return round(monthly_taxable_income * self.repayment_rate, 2)

    # Accumulate monthly interest
    def accumulate_interest(self):
        self.debt = round(self.debt + (self.interest / 12) * self.debt, 2)
        self.interest_accumulated = round(self.interest_accumulated + (self.interest / 12) * self.debt, 2)

    # Make the minimum repayment
    def make_minimum_repayment(self):

        if self.minimum_repayment > self.debt:
            print(f'{self.debt} < min repayment {self.minimum_repayment}')
            self.minimum_repayments_made += self.debt
            self.debt = 0
            return -1

        self.debt = round(self.debt - self.minimum_repayment, 2)
        self.minimum_repayments_made = round(self.minimum_repayments_made + self.minimum_repayment, 2)

    # Make an overpayment
    def make_repayment(self, amount):
        if amount > self.debt:
            print(f'{self.debt} < over_payment {amount}')
            self.overpayments_made += self.debt
            self.debt = 0

            return -1

        self.debt -= amount
        self.overpayments_made += amount

    def __repr__(self):
        return f"Debt({self.person.name.capitalize()}, {self.plan_type}, £{self.original_debt:,})"


def format_timediff(timediff):
    return f"{timediff.years} years, {timediff.months} months"


class Simulation:
    def __init__(self, debts: list, initial_state: dict):

        self.overpayments = None
        self.debts = debts
        self.initial_state = initial_state

        self.interest_accumulated = 0
        self.minimum_repayments_made = 0
        self.overpayments_made = 0
        self.paid = [debt.paid for debt in self.debts]
        self.time_left = relativedelta(0)

    def update(self, debt: Debt, updates: dict):
        print()
        print('Before:')
        print(debt.person.salary)
        print(self.overpayments)
        if 'salary' in updates:
            debt.person.salary = updates['salary']
            debt.minimum_repayment = debt.calculate_minimum_repayment()

        if 'overpayments' in updates:
            self.overpayments = updates['overpayments']

        print('After:')
        print(debt.person.salary)
        print(self.overpayments)

    def run(self, debt, overpayment=None, updates=None):
        while not debt.paid and debt.current_date < debt.expiry_date:

            # Increment by 1 month
            debt.current_date = debt.current_date + relativedelta(months=1)

            # If the new month is in the updates dict
            # then update the values
            if debt.current_date in updates.keys():
                to_do = updates[debt.current_date]
                self.update(debt, to_do)

            # Accumulate interest first
            debt.accumulate_interest()

            # Minimum repayment comes out (or pays off debt)
            if debt.make_minimum_repayment() == -1:
                debt.paid = True
                break

            # If overpayment is given else skip
            if overpayment:
                # Overpayment is made (or pays off debt)
                if debt.make_repayment(overpayment) == -1:
                    debt.paid = True
                    break

    def run_all(self, updates=None):

        for i, debt in enumerate(self.debts):
            self.update(debt, self.initial_state)
            self.run(debt, self.overpayments[i], updates)
            self.interest_accumulated = round(self.interest_accumulated + debt.interest_accumulated, 2)
            self.minimum_repayments_made = round(self.minimum_repayments_made + debt.minimum_repayments_made, 2)
            self.overpayments_made = round(self.overpayments_made + debt.overpayments_made, 2)
            self.paid[i] = debt.paid

        self.print_stats()

    def print_stats(self):
        table = [['Debt', 'Time Left To Pay Off', 'Minimum Repayments Made', 'Overpayments Made',
                  'Interest Accumulated', 'Total Paid', 'Paid off']]
        for debt in self.debts:
            row = [debt]

            time_diff = relativedelta(debt.current_date, debt.start_date)
            if time_diff.years > self.time_left.years:
                self.time_left = time_diff
            elif self.time_left.years == time_diff.years:
                if time_diff.months > self.time_left.months:
                    self.time_left = time_diff

            row.append(format_timediff(time_diff))
            row.append(f'{debt.minimum_repayments_made:,}')
            row.append(f'{debt.overpayments_made:,}')
            row.append(f'{debt.interest_accumulated:,}')
            row.append(f'{round(debt.minimum_repayments_made + debt.overpayments_made, 2):,}')
            row.append('Yes' if debt.paid else 'No')
            table.append(row)

        tab = PrettyTable(table[0])
        tab.add_row(table[1])
        tab.add_row(table[2], divider=True)

        row = ['Total', format_timediff(self.time_left), f'{self.minimum_repayments_made:,}',
               f'{self.overpayments_made:,}',
               f'{self.interest_accumulated:,}', f'{self.minimum_repayments_made + self.overpayments_made:,}',
               'All paid' if False not in self.paid else 'Not all paid']
        tab.add_row(row)
        print(tab)
