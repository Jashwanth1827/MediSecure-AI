INSURANCE_COMPANIES = {
    'hdfc_ergo': {
        'name': 'HDFC ERGO General Insurance',
        'claim_settlement_ratio': '98.5%',
        'incurred_claim_ratio': '75.2%',
        'network_hospitals': 12500,
        'founded': 2007,
        'plans': {
            'health_2_india_gold': {
                'name': 'Health 2 India Gold',
                'type': 'individual_family_floater',
                'coverage_range': '3L-50L',
                'starting_premium': 13750,
                'features': [
                    'Restoration of Sum Insured',
                    'No Claim Bonus up to 100%',
                    'Daycare procedures covered',
                    'Organ donor expenses',
                    'Pre and post hospitalization (60/90 days)',
                    'Domiciliary treatment',
                    'Air ambulance',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'families_comprehensive',
            },
            'my_health_optima': {
                'name': 'My:Health Optima',
                'type': 'individual_family_floater',
                'coverage_range': '3L-50L',
                'starting_premium': 10500,
                'features': [
                    'Restoration benefit',
                    'Health check-up every 2 years',
                    'Daily hospital cash (Rs.1000/day)',
                    'Wellness rewards',
                    'Pre and post hospitalization (60/90 days)',
                ],
                'waiting_period_ped': '2 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'As per sum insured',
                'best_for': 'budget_comprehensive',
            },
            'energy_plus': {
                'name': 'Energy Plus',
                'type': 'critical_illness',
                'coverage_range': '5L-25L',
                'starting_premium': 8000,
                'features': [
                    'Lump sum on critical illness diagnosis',
                    '13 critical illnesses covered',
                    'No medical check-up needed for entry',
                    'Tax benefits under 80D',
                ],
                'waiting_period_ped': '30 days',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'N/A',
                'best_for': 'critical_illness',
            },
        },
    },
    'icici_lombard': {
        'name': 'ICICI Lombard General Insurance',
        'claim_settlement_ratio': '97.2%',
        'incurred_claim_ratio': '78.5%',
        'network_hospitals': 8000,
        'founded': 2001,
        'plans': {
            'health_advantage': {
                'name': 'Health Advantage',
                'type': 'individual_family_floater',
                'coverage_range': '3L-1Cr',
                'starting_premium': 12000,
                'features': [
                    'Restore benefit (unlimited)',
                    'No Claim Bonus up to 100%',
                    'Free health check-ups',
                    'Wellness program rewards',
                    'Pre and post hospitalization (60/90 days)',
                    'Air ambulance cover',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'families_comprehensive',
            },
            'health_saver': {
                'name': 'Health Saver',
                'type': 'individual',
                'coverage_range': '5L-50L',
                'starting_premium': 6500,
                'features': [
                    'Individual policy (not floater)',
                    'Health rewards program',
                    'Domiciliary treatment',
                    'Daycare procedures',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'young_individuals',
            },
            'critical_illness_pro': {
                'name': 'Critical Illness Protect',
                'type': 'critical_illness',
                'coverage_range': '5L-50L',
                'starting_premium': 5000,
                'features': [
                    'Lump sum payout on diagnosis',
                    '38 critical illnesses covered',
                    'Survival period: 30 days',
                    'Renewable up to age 70',
                ],
                'waiting_period_ped': '90 days',
                'waiting_period_initial': '90 days',
                'room_rent_limit': 'N/A',
                'best_for': 'critical_illness',
            },
        },
    },
    'bajaj_allianz': {
        'name': 'Bajaj Allianz General Insurance',
        'claim_settlement_ratio': '97.8%',
        'incurred_claim_ratio': '72.4%',
        'network_hospitals': 7000,
        'founded': 2001,
        'plans': {
            'health_guard': {
                'name': 'Health Guard',
                'type': 'individual_family_floater',
                'coverage_range': '3L-50L',
                'starting_premium': 9000,
                'features': [
                    'Renewable up to age 80',
                    'No Claim Bonus up to 100%',
                    'Restoration benefit',
                    'Pre and post hospitalization (60/90 days)',
                    'Organ donor expenses',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'families_comprehensive',
            },
            'health_comcare': {
                'name': 'Health ComCare',
                'type': 'individual_family_floater',
                'coverage_range': '5L-100L',
                'starting_premium': 15000,
                'features': [
                    'Comprehensive cover',
                    'Modern treatment coverage',
                    'Bariatric surgery cover',
                    'Cataract surgery cover',
                    'Pre and post hospitalization (60/90 days)',
                ],
                'waiting_period_ped': '2 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'high_coverage',
            },
            'global_health_care': {
                'name': 'Global Health Care',
                'type': 'individual',
                'coverage_range': '25L-2Cr',
                'starting_premium': 50000,
                'features': [
                    'Worldwide coverage',
                    'Cashless treatment abroad',
                    'Second opinion worldwide',
                    'Emergency evacuation',
                    'High-end hospital network',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'international_coverage',
            },
        },
    },
    'star_health': {
        'name': 'Star Health and Allied Insurance',
        'claim_settlement_ratio': '96.5%',
        'incurred_claim_ratio': '82.1%',
        'network_hospitals': 14000,
        'founded': 2006,
        'plans': {
            'comprehensive_plan': {
                'name': 'Comprehensive Insurance Plan',
                'type': 'individual_family_floater',
                'coverage_range': '2L-50L',
                'starting_premium': 8000,
                'features': [
                    'Maternity cover after 2 years',
                    'No Claim Bonus up to 50%',
                    'Restoration benefit',
                    'Pre and post hospitalization (30/60 days)',
                    'Daycare procedures',
                ],
                'waiting_period_ped': '2 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'As per sum insured',
                'best_for': 'families_maternity',
            },
            'young_star': {
                'name': 'Young Star',
                'type': 'individual',
                'coverage_range': '5L-25L',
                'starting_premium': 4500,
                'features': [
                    'Affordable for young individuals (18-25)',
                    'No medical check-up needed',
                    'Daycare procedures covered',
                    'Auto restoration of sum insured',
                ],
                'waiting_period_ped': '2 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'General ward',
                'best_for': 'young_budget',
            },
            'senior_citizens_red_carpet': {
                'name': 'Senior Citizens Red Carpet',
                'type': 'senior_citizen',
                'coverage_range': '1L-10L',
                'starting_premium': 15000,
                'features': [
                    'Entry age up to 75 years',
                    'Pre-existing diseases covered from Day 1 (with loading)',
                    'Daycare procedures',
                    'Free health check-ups',
                    'No upper age limit for renewal',
                ],
                'waiting_period_ped': '1 year (can buy RID to reduce)',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'General ward',
                'best_for': 'senior_citizens',
            },
            'super_surplus': {
                'name': 'Super Surplus (Top-Up)',
                'type': 'top_up',
                'coverage_range': '10L-1Cr',
                'starting_premium': 3500,
                'features': [
                    'Top-up plan for existing base policy',
                    'Low premium for high coverage',
                    'Deductible options available',
                    'Family floater option',
                ],
                'waiting_period_ped': 'None (inherits from base)',
                'waiting_period_initial': 'None',
                'room_rent_limit': 'As per base policy',
                'best_for': 'top_up',
            },
        },
    },
    'max_bupa': {
        'name': 'Niva Bupa Health Insurance (formerly Max Bupa)',
        'claim_settlement_ratio': '98.1%',
        'incurred_claim_ratio': '70.5%',
        'network_hospitals': 10000,
        'founded': 2010,
        'plans': {
            'reassure': {
                'name': 'ReAssure',
                'type': 'individual_family_floater',
                'coverage_range': '5L-50L',
                'starting_premium': 11000,
                'features': [
                    'Lifetime renewability',
                    'No Claim Bonus up to 100%',
                    'Unlimited restoration',
                    'Lock the clock (premium locks at entry age)',
                    'SafeGuard add-on',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'long_term_value',
            },
            'go_wise': {
                'name': 'GoWise',
                'type': 'individual',
                'coverage_range': '3L-25L',
                'starting_premium': 7500,
                'features': [
                    'Customizable plan (pay for what you need)',
                    'No Claim Bonus up to 50%',
                    'Wellness program',
                    'Daycare procedures',
                    'OPD cover available',
                ],
                'waiting_period_ped': '2 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'As per option chosen',
                'best_for': 'budget_customizable',
            },
            'artemis_basic': {
                'name': 'Artemis Basic',
                'type': 'individual_family_floater',
                'coverage_range': '3L-50L',
                'starting_premium': 9500,
                'features': [
                    'No loading for individual health history',
                    'No medical screening up to 45 years',
                    'Free health check-ups',
                    'Wellness rewards',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'families_no_loading',
            },
        },
    },
    'care_health': {
        'name': 'Care Health Insurance',
        'claim_settlement_ratio': '97.5%',
        'incurred_claim_ratio': '76.8%',
        'network_hospitals': 11000,
        'founded': 1997,
        'plans': {
            'care_supreme': {
                'name': 'Care Supreme',
                'type': 'individual_family_floater',
                'coverage_range': '5L-50L',
                'starting_premium': 10000,
                'features': [
                    'Cumulative bonus up to 100%',
                    'Unlimited automatic recharge',
                    'Bariatric surgery cover',
                    'Domiciliary treatment',
                    'Air ambulance',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'families_comprehensive',
            },
            'care_essentials': {
                'name': 'Care Essentials',
                'type': 'individual_family_floater',
                'coverage_range': '3L-10L',
                'starting_premium': 6000,
                'features': [
                    'Affordable basic coverage',
                    'Pre and post hospitalization (30/60 days)',
                    'Daycare procedures',
                    'No medical check-up up to 50 years',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'General ward',
                'best_for': 'budget_basic',
            },
            'care_supreme_global': {
                'name': 'Care Supreme Global',
                'type': 'individual',
                'coverage_range': '50L-2Cr',
                'starting_premium': 35000,
                'features': [
                    'Worldwide coverage',
                    'Cashless treatment abroad',
                    'Second opinion worldwide',
                    'Emergency evacuation',
                    'Top hospitals globally',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'international_coverage',
            },
        },
    },
    'reliance_general': {
        'name': 'Reliance General Insurance',
        'claim_settlement_ratio': '95.8%',
        'incurred_claim_ratio': '73.6%',
        'network_hospitals': 6500,
        'founded': 2000,
        'plans': {
            'health_infinity': {
                'name': 'Health Infinity',
                'type': 'individual_family_floater',
                'coverage_range': '3L-6L (unlimited with restoration)',
                'starting_premium': 8500,
                'features': [
                    'Unlimited sum insured restoration',
                    'No Claim Bonus up to 100%',
                    'Pre and post hospitalization (60/90 days)',
                    'Daycare procedures',
                    'Organ donor expenses',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'unlimited_coverage',
            },
            'health_access': {
                'name': 'Health Access',
                'type': 'individual_family_floater',
                'coverage_range': '2L-25L',
                'starting_premium': 5500,
                'features': [
                    'Affordable family coverage',
                    'No medical check-up up to 45 years',
                    'Daycare procedures',
                    'Pre and post hospitalization (30/60 days)',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'As per sum insured',
                'best_for': 'budget_families',
            },
        },
    },
    'manipalcigna': {
        'name': 'ManipalCigna Health Insurance',
        'claim_settlement_ratio': '96.9%',
        'incurred_claim_ratio': '68.2%',
        'network_hospitals': 8500,
        'founded': 2012,
        'plans': {
            'manipalcigna_2_in_1': {
                'name': 'ManipalCigna 2 in 1',
                'type': 'individual_family_floater',
                'coverage_range': '3L-50L',
                'starting_premium': 9500,
                'features': [
                    'Double sum insured on first claim',
                    'No Claim Bonus up to 100%',
                    'Wellness program',
                    'Tele-consultation',
                    'Second medical opinion',
                ],
                'waiting_period_ped': '2 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'double_coverage',
            },
            'lifetime_health': {
                'name': 'Lifetime Health',
                'type': 'individual',
                'coverage_range': '5L-50L',
                'starting_premium': 7000,
                'features': [
                    'Lifetime renewability',
                    'Cumulative bonus up to 50%',
                    'No medical check-up up to 45 years',
                    'Free annual health check-up',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'No limit',
                'best_for': 'long_term_individual',
            },
        },
    },
    'national_insurance': {
        'name': 'National Insurance Company (Govt PSU)',
        'claim_settlement_ratio': '93.2%',
        'incurred_claim_ratio': '85.5%',
        'network_hospitals': 4000,
        'founded': 1906,
        'plans': {
            'mediclaim': {
                'name': 'Mediclaim Policy',
                'type': 'individual_family_floater',
                'coverage_range': '1L-10L',
                'starting_premium': 4000,
                'features': [
                    'Government-backed insurer',
                    'Most affordable premiums',
                    'Domiciliary treatment',
                    'Pre and post hospitalization (30/60 days)',
                    'AYUSH treatment covered',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'As per sum insured',
                'best_for': 'budget_govt',
            },
        },
    },
    'oriental_insurance': {
        'name': 'Oriental Insurance Company (Govt PSU)',
        'claim_settlement_ratio': '91.8%',
        'incurred_claim_ratio': '87.3%',
        'network_hospitals': 3500,
        'founded': 1947,
        'plans': {
            'health_insurance': {
                'name': 'Health Insurance Policy',
                'type': 'individual_family_floater',
                'coverage_range': '50K-10L',
                'starting_premium': 3500,
                'features': [
                    'Government-backed insurer',
                    'Very low premiums',
                    'Pre and post hospitalization (30/60 days)',
                    'Daycare procedures',
                    'AYUSH treatment',
                ],
                'waiting_period_ped': '3 years',
                'waiting_period_initial': '30 days',
                'room_rent_limit': 'General ward',
                'best_for': 'ultra_budget',
            },
        },
    },
}

def get_all_companies():
    return list(INSURANCE_COMPANIES.keys())

def get_company(company_id):
    return INSURANCE_COMPANIES.get(company_id)

def get_all_plans():
    plans = []
    for company_id, company in INSURANCE_COMPANIES.items():
        for plan_id, plan in company['plans'].items():
            plans.append({
                'company_id': company_id,
                'company_name': company['name'],
                'plan_id': plan_id,
                'plan_name': plan['name'],
                'type': plan['type'],
                'coverage_range': plan['coverage_range'],
                'starting_premium': plan['starting_premium'],
                'features': plan['features'],
                'waiting_period_ped': plan['waiting_period_ped'],
                'best_for': plan['best_for'],
            })
    return plans

def filter_plans(criteria):
    matching_plans = []
    all_plans = get_all_plans()

    for plan in all_plans:
        score = 0
        reasons = []

        plan_type = plan['type']
        best_for = plan['best_for']
        premium = plan['starting_premium']
        csr = INSURANCE_COMPANIES[plan['company_id']]['claim_settlement_ratio']

        if criteria.get('budget') == 'low' and premium < 6000:
            score += 3
            reasons.append('Low premium (under Rs.6,000)')
        elif criteria.get('budget') == 'medium' and 6000 <= premium <= 12000:
            score += 3
            reasons.append('Mid-range premium')
        elif criteria.get('budget') == 'high' and premium >= 10000:
            score += 3
            reasons.append('Premium coverage plan')

        if criteria.get('coverage_type') == 'family' and 'family' in plan_type:
            score += 2
            reasons.append('Suitable for family coverage')
        elif criteria.get('coverage_type') == 'individual' and 'individual' in plan_type:
            score += 2
            reasons.append('Suitable for individual')

        if criteria.get('needs_maternity') and 'maternity' in best_for:
            score += 3
            reasons.append('Maternity coverage available')

        if criteria.get('needs_critical_illness') and 'critical' in plan_type:
            score += 4
            reasons.append('Dedicated critical illness coverage')

        if criteria.get('needs_senior') and 'senior' in plan_type:
            score += 5
            reasons.append('Designed for senior citizens')

        if criteria.get('needs_international') and 'international' in best_for:
            score += 4
            reasons.append('International coverage available')

        if criteria.get('needs_topup') and 'top_up' in plan_type:
            score += 4
            reasons.append('Top-up plan for existing coverage')

        csr_num = float(csr.replace('%', ''))
        if csr_num >= 97:
            score += 2
            reasons.append(f'High claim settlement ratio ({csr})')

        if criteria.get('has_diabetes') or criteria.get('has_heart_disease'):
            if plan['waiting_period_ped'] in ['1 year (can buy RID to reduce)', '2 years']:
                score += 2
                reasons.append('Shorter PED waiting period')

        matching_plans.append({
            'score': score,
            'reasons': reasons,
            **plan
        })

    matching_plans.sort(key=lambda x: x['score'], reverse=True)
    return [p for p in matching_plans if p['score'] > 0][:8]
