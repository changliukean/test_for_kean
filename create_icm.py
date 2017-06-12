import mysql.connector
from mysql.connector import errorcode

import datetime
from datetime import datetime

import utilities as u


cnx = mysql.connector.connect(user='Andrew', password='Kindle01', database = 'kean')
cursor_get = cnx.cursor()
cursor_load = cnx.cursor()

scenario = 'ICM - Blackstone'
company = 'Lightstone'
power_plant_entities = ['Gavin', 'Waterford', 'Lawrenceburg', 'Darby']
valuation_date = '2016-10-17'   #use date of BX investment committee approval

''' reconcile total portfolio generation '''
periods = [datetime(2017, 12, 31), datetime(2018, 12, 31), datetime(2019, 12, 31), datetime(2020, 12, 31), datetime(2021, 12, 31), datetime(2022, 12, 31), datetime(2023, 12, 31)]

for period in periods:
    generation = 0
    for entity in power_plant_entities:
        nameplate = u.get_scenario_assumption(scenario, company, entity,
                'Nameplate Capacity', period, period)

        on_peak_hours = u.get_scenario_assumption(scenario, company, 'Lightstone',
                'On Peak Hours', period, period)

        off_peak_hours = u.get_scenario_assumption(scenario, company, 'Lightstone',
                'Off Peak Hours', period, period)

        realized_on_peak_capacity_factor = u.get_scenario_assumption(scenario, company,
                entity, 'Realized On Peak Capacity Factor', period, period)

        realized_off_peak_capacity_factor = u.get_scenario_assumption(scenario, company,
                entity, 'Realized Off Peak Capacity Factor', period, period)

        on_peak_generation = nameplate * on_peak_hours * realized_on_peak_capacity_factor
        off_peak_generation = nameplate * off_peak_hours * realized_off_peak_capacity_factor
        total_generation = on_peak_generation + off_peak_generation

        #u.load_financials_fsli(scenario, company, entity, 'On Peak Generation', period, on_peak_generation)
        #u.load_financials_fsli(scenario, company, entity, 'Off Peak Generation', period, off_peak_generation)

        instrument_id = entity + ' Realized Power Price - Calendar Strip On Peak'
        realized_price_on_peak = u.get_price(scenario, valuation_date, instrument_id, period)

        instrument_id = entity + ' Realized Power Price - Calendar Strip Off Peak'
        realized_price_off_peak = u.get_price(scenario, valuation_date, instrument_id, period)

        energy_revenue_on_peak = on_peak_generation * realized_price_on_peak
        energy_revenue_off_peak = off_peak_generation * realized_price_off_peak

        #u.load_financials_fsli(scenario, company, entity, 'On Peak Energy Revenue', period, energy_revenue_on_peak)
        #u.load_financials_fsli(scenario, company, entity, 'Off Peak Energy Revenue', period, energy_revenue_off_peak)
        #u.load_financials_fsli(scenario, company, entity, 'Energy Revenue', period, energy_revenue_on_peak+energy_revenue_off_peak)

        capacity_period_end_front = datetime(period.year, 5, 31)
        capacity_revenue_front = u.get_cleared_capacity_revenue(scenario, company, entity, capacity_period_end_front)
        capacity_period_end_back = datetime(period.year + 1, 5, 31)
        capacity_revenue_back = u.get_cleared_capacity_revenue(scenario, company, entity, capacity_period_end_back)


        period_uncleared_capacity = datetime(period.year, 1, 31)
        capacity_revenue_uncleared = 0.0
        while period_uncleared_capacity <= period:
            capacity_uncleared = u.get_scenario_assumption(scenario, company, entity,
                'Uncleared Capacity', period_uncleared_capacity, period_uncleared_capacity)

            if capacity_uncleared is not None:
                capacity_uncleared_price = u.get_price(scenario, valuation_date, 'Capacity - PJM RTO', period_uncleared_capacity)
                capacity_revenue_uncleared += capacity_uncleared * capacity_uncleared_price * period_uncleared_capacity.day

            period_uncleared_capacity = u.calc_next_month_end(period_uncleared_capacity)


        if capacity_revenue_front is not None and capacity_revenue_back is not None:
            capacity_revenue = ((5/12) * capacity_revenue_front + (7/12) * capacity_revenue_back) * 365 + capacity_revenue_uncleared
        elif capacity_revenue_front is not None:
            capacity_revenue = (5/12) * capacity_revenue_front* 366 + capacity_revenue_uncleared
        else:
            capacity_revenue = capacity_revenue_uncleared

        #u.load_financials_fsli(scenario, company, entity, 'Capacity Revenue', period, capacity_revenue)

        ''' Load totals '''
        gross_energy_margin = u.calc_financials_subtotal(scenario, company, entity, 'Gross Energy Margin', period)
        #u.load_financials_fsli(scenario, company, entity, 'Gross Energy Margin', period, gross_energy_margin)

        net_energy_margin = u.calc_financials_subtotal(scenario, company, entity, 'Net Energy Margin', period)
        #u.load_financials_fsli(scenario, company, entity, 'Net Energy Margin', period, net_energy_margin)

        total_other_income = u.calc_financials_subtotal(scenario, company, entity, 'Total Other Income', period)
        #u.load_financials_fsli(scenario, company, entity, 'Total Other Income', period, total_other_income)

        gross_margin = u.calc_financials_subtotal(scenario, company, entity, 'Gross Margin', period)
        #u.load_financials_fsli(scenario, company, entity, 'Gross Margin', period, gross_margin)

        fixed_non_labor = u.calc_financials_subtotal(scenario, company, entity, 'Fixed Non-Labor Expense', period)
        #u.load_financials_fsli(scenario, company, entity, 'Fixed Non-Labor Expense', period, fixed_non_labor)

        total_fixed_costs = u.calc_financials_subtotal(scenario, company, entity, 'Total Fixed Costs', period)
        #u.load_financials_fsli(scenario, company, entity, 'Total Fixed Costs', period, total_fixed_costs)

        ebitda = u.calc_financials_subtotal(scenario, company, entity, 'EBITDA', period)
        #u.load_financials_fsli(scenario, company, entity, 'EBITDA', period, ebitda)

        total_capex = u.calc_financials_subtotal(scenario, company, entity, 'Total Capex', period)
        #u.load_financials_fsli(scenario, company, entity, 'Total Capex', period, total_capex)

        ebitda_less_capex = u.calc_financials_subtotal(scenario, company, entity, 'EBITDA less Capex', period)
        #u.load_financials_fsli(scenario, company, entity, 'EBITDA less Capex', period, ebitda_less_capex)
