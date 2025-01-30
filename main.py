from objects import Person, Debt, Simulation
from datetime import date

adam = Person(42000, 'adam')

ug = Debt(46800, 2022, adam, 'plan 2')
pg = Debt(13000, 2023, adam, 'postgraduate')

# possible to update salary, overpayments
initial = {
    'salary': 42000,
    'overpayments': [None, 150]
}

updates = {
    date(2026, 1, 1): {
        'salary': 50000,
        'overpayments': [200, 0]
    }
}

sim = Simulation([ug, pg], initial)
sim.run_all(updates)

