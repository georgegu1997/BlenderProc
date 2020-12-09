
from sys import version_info
if version_info.major == 2:
    raise Exception("This script only works with python3.x!")

import os
import csv
import urllib
from urllib.request import urlretrieve, build_opener, install_opener
import subprocess

OBJECT_NAMES = ["3m_high_tack_spray_adhesive", "advil_liqui_gels", "aunt_jemima_original_syrup", "bai5_sumatra_dragonfruit", "band_aid_clear_strips", "band_aid_sheer_strips", "blue_clover_baby_toy", "bumblebee_albacore", "campbells_chicken_noodle_soup", "campbells_soup_at_hand_creamy_tomato", "canon_ack_e10_box", "cheez_it_white_cheddar", "chewy_dipps_chocolate_chip", "chewy_dipps_peanut_butter", "cholula_chipotle_hot_sauce", "cinnamon_toast_crunch", "clif_crunch_chocolate_chip", "clif_crunch_peanut_butter", "clif_crunch_white_chocolate_macademia_nut", "clif_z_bar_chocolate_chip", "clif_zbar_chocolate_brownie", "coca_cola_glass_bottle", "coffee_mate_french_vanilla", "colgate_cool_mint", "crayola_24_crayons", "crayola_yellow_green", "crest_complete_minty_fresh", "crystal_hot_sauce", "cup_noodles_chicken", "cup_noodles_shrimp_picante", "detergent", "dove_beauty_cream_bar", "dove_go_fresh_burst", "dove_pink", "eating_right_for_healthy_living_apple", "eating_right_for_healthy_living_blueberry", "eating_right_for_healthy_living_mixed_berry", "eating_right_for_healthy_living_raspberry", "expo_marker_red", "fruit_by_the_foot", "gushers_tropical_flavors", "haagen_dazs_butter_pecan", "haagen_dazs_cookie_dough", "hersheys_bar", "hersheys_cocoa", "honey_bunches_of_oats_honey_roasted", "honey_bunches_of_oats_with_almonds", "hunts_paste", "hunts_sauce", "ikea_table_leg_blue", "krylon_crystal_clear", "krylon_low_odor_clear_finish", "krylon_matte_finish", "krylon_short_cuts", "listerine_green", "mahatma_rice", "mom_to_mom_butternut_squash_pear", "mom_to_mom_sweet_potato_corn_apple", "motts_original_assorted_fruit", "nature_valley_crunchy_oats_n_honey", "nature_valley_crunchy_variety_pack", "nature_valley_gluten_free_roasted_nut_crunch_almond_crunch", "nature_valley_granola_thins_dark_chocolate", "nature_valley_soft_baked_oatmeal_squares_cinnamon_brown_sugar", "nature_valley_soft_baked_oatmeal_squares_peanut_butter", "nature_valley_sweet_and_salty_nut_almond", "nature_valley_sweet_and_salty_nut_cashew", "nature_valley_sweet_and_salty_nut_peanut", "nature_valley_sweet_and_salty_nut_roasted_mix_nut", "nice_honey_roasted_almonds", "nutrigrain_apple_cinnamon", "nutrigrain_blueberry", "nutrigrain_cherry", "nutrigrain_chotolatey_crunch", "nutrigrain_fruit_crunch_apple_cobbler", "nutrigrain_fruit_crunch_strawberry_parfait", "nutrigrain_harvest_blueberry_bliss", "nutrigrain_harvest_country_strawberry", "nutrigrain_raspberry", "nutrigrain_strawberry", "nutrigrain_strawberry_greek_yogurt", "nutrigrain_toffee_crunch_chocolatey_toffee", "palmolive_green", "palmolive_orange", "paper_cup_holder", "paper_plate", "pepto_bismol", "pop_secret_butter", "pop_secret_light_butter", "pop_tarts_strawberry", "pringles_bbq", "progresso_new_england_clam_chowder", "quaker_big_chewy_chocolate_chip", "quaker_big_chewy_peanut_butter_chocolate_chip", "quaker_chewy_chocolate_chip", "quaker_chewy_dipps_peanut_butter_chocolate", "quaker_chewy_low_fat_chocolate_chunk", "quaker_chewy_peanut_butter", "quaker_chewy_peanut_butter_chocolate_chip", "quaker_chewy_smores", "red_bull", "red_cup", "ritz_crackers", "softsoap_clear", "softsoap_gold", "softsoap_green", "softsoap_purple", "softsoap_white", "south_beach_good_to_go_dark_chocolate", "south_beach_good_to_go_peanut_butter", "spam", "spongebob_squarepants_fruit_snaks", "suave_sweet_guava_nectar_body_wash", "sunkist_fruit_snacks_mixed_fruit", "tapatio_hot_sauce", "v8_fusion_peach_mango", "v8_fusion_strawberry_banana", "vo5_extra_body_volumizing_shampoo", "vo5_split_ends_anti_breakage_shampoo", "vo5_tea_therapy_healthful_green_tea_smoothing_shampoo", "white_rain_sensations_apple_blossom_hydrating_body_wash", "white_rain_sensations_ocean_mist_hydrating_body_wash", "white_rain_sensations_ocean_mist_hydrating_conditioner", "windex", "zilla_night_black_heat"]

if __name__ == "__main__":
    # setting the default header, else the server does not allow the download
    opener = build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    install_opener(opener)

    # set the download directory relative to this one
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bigbird_dir = os.path.join(current_dir, "..", "resources", "bigbird")

    if not os.path.exists(bigbird_dir):
        os.makedirs(bigbird_dir)

    for obj_name in OBJECT_NAMES:
        processed_url = "http://rll.berkeley.edu/bigbird/aliases/7c32cd7e8f/export/%s/processed.tgz" % obj_name
        current_file_path = os.path.join(bigbird_dir, "%s_processed.tgz" % obj_name)
        
    