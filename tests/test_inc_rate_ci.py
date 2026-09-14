from incidence_prevalence.incidence_partial import inc_rate_ci_exact


def test_inc_rate_ci_correct():
    outcome_counts = [
        12,
        10,
        14,
        8,
        18,
        7,
        4,
        2,
        5,
        3,
        14,
        22,
        26,
        21,
        28,
        37,
        72,
        88,
        110,
    ]
    person_years = [
        4320.643,
        4627.608,
        4977.161,
        5324.561,
        5722.93,
        6165.481,
        6781.563,
        7438.533,
        8248.523,
        9215.934,
        10380.011,
        11619.483,
        13058.836,
        14600.676,
        16299.548,
        17988.049,
        19923.962,
        21981.886,
        24332.676,
    ]
    incidence_100000_pys_95CI_lower = [
        143.51,
        103.626,
        153.781,
        64.866,
        186.407,
        45.647,
        16.071,
        3.256,
        19.682,
        6.713,
        73.737,
        118.657,
        130.058,
        89.032,
        114.149,
        144.826,
        282.753,
        321.076,
        371.544,
    ]
    incidence_100000_pys_95CI_upper = [
        485.15,
        397.405,
        471.948,
        296.047,
        497.084,
        233.926,
        151.021,
        97.125,
        141.46,
        95.132,
        226.297,
        286.659,
        291.726,
        219.858,
        248.276,
        283.519,
        455.091,
        493.217,
        544.863,
    ]
    assert [
        round(float(inc_rate_ci_exact(0.025, ev, pt)), 3)
        for ev, pt in zip(outcome_counts, person_years)
    ] == incidence_100000_pys_95CI_lower
    assert [
        round(float(inc_rate_ci_exact(0.975, ev+1, pt)), 3)
        for ev, pt in zip(outcome_counts, person_years)
    ] == incidence_100000_pys_95CI_upper
