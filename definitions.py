### Definitions for Inputs + Predetermined Values in Acquisition Scenario
definitions = {
    'periods' : {
        'def' : '''
        Number of periods for investment scenario.
        ''',
        'value' : 8
    },
    'discountRate' : {
        'def' : '''
        Rate to use for the NPV (Net Present Value) of the investment.
        ''',
        'value' : 8.00
    },
    'inflationRate' : {
        'def' : '''
        Yearly inflation rate. It can be modified year by year in the table below. 
        ''',
        'value' : 2.00
    },
    'monthlyCharge' : {
        'def' : '''
        Monthly fee charged to clients for using the radiolink.
        ''',
        'value' : 250
    },
    'setUpCost' : {
        'def' : '''
        Fee charged to client whenever the relocate a radiolink.
        ''',
        'value' : 1500
    },
    'opsMaintAnnual' : {
        'def' : '''
        Operations and Maintenance Fees (per radiolink)
        ''',
        'value' : 450
    },
    'itTotalAnnual' : {
        'def' : '''
        Annual IT Costs for the entire radiolink base.
        ''',
        'value' : 35000
    },
    'otherCostsPct' : {
        'def' : '''
        Other annual costs accounted as a percentage of the total revenue.
        ''',
        'value' : 1.5
    },
    'upfrontOffer' : {
        'def' : '''
        Buying offer for each radiolink.
        ''',
        'value' : 10000
    },
    'bandTransfer' : {
        'def' : '''
        Cost of migrating a radiolink to one of our owned frequencies.
        ''',
        'value' : 8500
    },
    'costChurned' : {
        'def' : '''
        Cost for a radiolink being churned.
        ''',
        'value' : 5500
    },
    'itSetUpCapex' : {
        'def' : '''
        IT Setup costs for the entire radiolink base.
        ''',
        'value' : 125000
    },
}
