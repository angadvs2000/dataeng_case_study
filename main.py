from crash_analysis import CrashAnalytics


def main():
    analytics = CrashAnalytics()

    # Q1
    print("Analytics 1: ", analytics.crashes_with_more_than_2_males_killed())

    # Q2
    print("Analytics 2: ", analytics.two_wheelers_booked_count())

    # Q3
    print("Analytics 3: ", analytics.top_car_makes_with_fatal_crashes_and_no_airbag())

    # Q4
    print("Analytics 4: ", analytics.veh_with_valid_lic_driver_and_hnr())

    # Q5
    print("Analytics 5: ", analytics.state_with_highest_acccidents_without_females())

    # Q6
    print("Analytics 6: ", analytics.top_3rdto5th_veh_makes_with_largest_total_injuries_incl_death())

    # Q7
    print("Analytics 7: ", analytics.top_ethnicity_of_each_body_style())

    # Q8
    print("Analytics 8: ", analytics.top_5_zipcodes_with_alc_as_contrib_factr())

    # Q9
    print("Analytics 9: ", analytics.crashes_with_damaged_prop_and_damage_level_above_4_with_insured_car())

    # Q10
    print("Analytics 10: ", analytics.top_veh_makes_in_speeding_accidents())


if __name__ == "__main__":
    main()