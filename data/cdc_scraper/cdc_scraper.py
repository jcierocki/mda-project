import pandas as pd
from sodapy import Socrata
from tqdm import tqdm

cdc_dict = {
    'mask_mandates' : {
        'table_name' : '42jj-z7fa',
        'query' : '''
             state_tribe_territory as state_code
            , county_name
            , fips_code::text
            , substring(left_pad(fips_code::text,5,'0'),0,3) as state_fips
            , substring(left_pad(fips_code::text,5,'0'),3,5) as county_fips
            , date
            , face_masks_required_in_public
        '''
    },
    'stay_at_home' : {
        'table_name' : 'qz3x-mf9n',
        'query' : '''
             state_tribe_territory as state_code
            , county_name
            , left_pad(fips_state::text,2,'0') as state_fips
            , left_pad(fips_county::text,3,'0') as county_fips
            , date
            , current_order_status
        '''
    },
    'gathering_bans' : {
        'table_name' : '7xvh-y5vh',
        'query' : '''
             state_tribe_territory as state_code
            , county_name
            , left_pad(fips_state::text,2,'0') as state_fips
            , left_pad(fips_county::text,3,'0') as county_fips
            , date
            , general_gb_order_group
            , general_gb_order_code
            , general_or_under_6ft_bans_gatherings_over
            , indoor_outdoor
        '''
    },
    'bar_closings' : {
        'table_name' : '9kjw-3miq',
        'query' : '''
             state_tribe_territory as state_code
            , county_name
            , left_pad(fips_state::text,2,'0') as state_fips
            , left_pad(fips_county::text,3,'0') as county_fips
            , date
            , business_type
            , action
            , percent_capacity_outdoor
            , percent_capacity_indoor
            , numeric_capacity_outdoor
            , numeric_capacity_indoor
            , limited_open_outdoor_only
            , limited_open_general_indoor
        '''
    },
    'restaurant_closings' : {
        'table_name' : 'azmd-939x',
        'query' : '''
             state_tribe_territory as state_code
            , county_name
            , left_pad(fips_state::text,2,'0') as state_fips
            , left_pad(fips_county::text,3,'0') as county_fips
            , date
            , business_type
            , action
            , percent_capacity_outdoor
            , percent_capacity_indoor
            , numeric_capacity_outdoor
            , numeric_capacity_indoor
            , limited_open_outdoor_only
            , limited_open_general_indoor
        '''
    },
    'community_transmission' : {
        'table_name' : 'nra9-vzzn',
        'query' : '''
             state_name as state_code
            , county_name
            , fips_code::text
            , substring(fips_code::text,1,2) as state_fips
            , substring(fips_code::text,3,5) as county_fips
            , date
            , cases_per_100k_7_day_count
            , percent_test_results_reported
            , community_transmission_level
        '''
    },
    'vaccinations' : {
        'table_name' : '8xkx-amqh',
        'query' : '''
             *
        '''
    },
    'vaccine_hesitancy' : {
        'table_name' : 'q9mh-h2tw',
        'query' : '''
        fips_code::text
        , substring(left_pad(fips_code::text,5,'0'),0,3) as state_fips
        , substring(left_pad(fips_code::text,5,'0'),3,5) as county_fips
        , county_name
        , state
        , estimated_hesitant
        , estimated_hesitant_or_unsure
        , estimated_strongly_hesitant
        , social_vulnerability_index
        , svi_category
        , ability_to_handle_a_covid
        , cvac_category
        , percent_adults_fully
        , percent_hispanic
        , percent_non_hispanic_american
        , percent_non_hispanic_asian
        , percent_non_hispanic_black
        , percent_non_hispanic_native
        , percent_non_hispanic_white
        , geographical_point
        , state_code
        , county_boundary
        , state_boundary
        '''
    }
}

for file in tqdm(cdc_dict):
    results = client.get(f"{cdc_dict[file]['table_name']}",
                     select =f"{cdc_dict[file]['query']}",
                     limit = 3000000)
    results_df = pd.DataFrame.from_records(results)
    results_df.to_csv(f"data/cdc_{file}.csv",index=False)
