from sqlalchemy.sql import text
from model import engine

def create_view(name, query, **kwargs):
    stm_delete = f"""
    DROP VIEW IF EXISTS {name}
    """

    with engine.connect() as connection:
        connection.execute(stm_delete)

    stm_create = text(f"""
    CREATE VIEW {name} AS 
    {query}
    """)

    with engine.connect() as connection:
        connection.execute(stm_create, **kwargs)

current_ratios_to_open = '''
    SELECT 	f.symbol as future_symbol,
            fp.bid_price as future_price,
            s.symbol as spot_symbol,
            sp.ask_price as spot_price,
            ((fp.bid_price / sp.ask_price - 1) * 100) as direct_ratio,
            TIMESTAMPDIFF(HOUR, now(), f.delivery_date) + 1 as hours,
            ((fp.bid_price / sp.ask_price - 1) * 100) / (TIMESTAMPDIFF(HOUR, now(), f.delivery_date) + 1) as hour_ratio,
            TIMESTAMPDIFF(DAY, now(), f.delivery_date) days,
            ((fp.bid_price / sp.ask_price - 1) * 100) / (TIMESTAMPDIFF(hour, now(), f.delivery_date) + 1)  * 24 * 365 as year_ratio,
            f.contract_size,
            f.contract_size / fp.bid_price as buy_per_contract,
            s.tick_size,
            s.base_asset,
            cs.signal
    FROM 	spot s
    JOIN 	spot_price sp
    ON		s.symbol = sp.symbol
    JOIN 	future f
    ON		s.symbol = concat(f.pair, 'T')
    JOIN 	future_price fp
    ON		f.symbol = fp.symbol
    JOIN    current_signal cs
    ON      f.symbol = cs.symbol
    WHERE	f.symbol NOT LIKE "%_PERP"
            AND	delivery_date > now()
    ORDER BY
            year_ratio DESC
    '''

current_ratios_to_close = '''
    SELECT 	f.symbol as future_symbol,
            fp.ask_price as future_price,
            s.symbol as spot_symbol,
            sp.bid_price as spot_price,
            ((fp.ask_price / sp.bid_price - 1) * 100) as direct_ratio,
            TIMESTAMPDIFF(HOUR, now(), f.delivery_date) + 1 as hours,
            ((fp.ask_price / sp.bid_price - 1) * 100) / (TIMESTAMPDIFF(HOUR, now(), f.delivery_date) + 1) as hour_ratio,
            TIMESTAMPDIFF(DAY, now(), f.delivery_date) days,
            ((fp.ask_price / sp.bid_price - 1) * 100) / (TIMESTAMPDIFF(hour, now(), f.delivery_date) + 1)  * 24 * 365 as year_ratio,
            f.contract_size,
            f.contract_size / fp.ask_price as buy_per_contract,
            s.tick_size,
            s.base_asset,
            cs.signal
    FROM 	spot s
    JOIN 	spot_price sp
    ON		s.symbol = sp.symbol
    JOIN 	future f
    ON		s.symbol = concat(f.pair, 'T')
    JOIN 	future_price fp
    ON		f.symbol = fp.symbol
    JOIN    current_signal cs
    ON      f.symbol = cs.symbol
    WHERE	f.symbol NOT LIKE "%_PERP"
            AND	delivery_date > now()
    ORDER BY
            year_ratio DESC
    '''


current_operations_to_open = '''
    SELECT	 	pos.id as position_id, 
    			cr.*, 
    			round(least(c2.value, sb.free) / f.contract_size) contract_qty, 
    			fb.cross_wallet_balance as future_balance
    FROM 		current_ratios cr
    JOIN		future f
    ON			cr.future_symbol = f.symbol
    JOIN 		configuration c1
    ON			c1.name = 'min_operation_value'
    JOIN 		configuration c2
    ON			c2.name = 'max_operation_value'
    JOIN 		spot_balance sb
    ON			sb.asset='USDT' and sb.outdated = 0
    JOIN		spot s
    ON			cr.spot_symbol = s.symbol
    JOIN 		future_balance fb
    on			s.base_asset = fb.asset
    LEFT JOIN 	(select max(id) as id, p.future from position p where p.state = 'CREATED' group by  p.future) pos
    ON			cr.future_symbol = pos.future
'''


future_trade_grouped = '''
    select 		future_order_id, 
                sum(base_qty) as base_qty, 
                sum(commission) as commission, 
                count(*) as trades_count
    from 		future_trade
    group by	future_order_id
    '''

current_operations_to_close = '''
    select 		avg_open_ratios.position_id, 
                avg_open_ratios.direct_ratio open_avg_direct_ratio,  
                avg_open_ratios.year_ratio open_avg_year_ratio,  
                avg_open_ratios.direct_ratio - crtc.direct_ratio direct_ratio_diff,  
                avg_open_ratios.year_ratio - crtc.year_ratio year_ratio_diff, 
                crtc.*,
                -fp.position_amount as contract_qty,
                crto.future_symbol as better_future_symbol,
                crto.direct_ratio as better_direct_ratio,
                crto.year_ratio as better_year_ratio
    from 		current_ratios_to_close crtc
    join 
    (select 	
                o.position_id, 
                min(o.future) as future, 
                sum(o.direct_ratio*o.contract_qty) / sum(o.contract_qty) direct_ratio, 
                sum(o.year_ratio*o.contract_qty) / sum(o.contract_qty) year_ratio,
                (select future_symbol 
                from current_ratios_to_open co 
                where co.future_symbol != min(o.future)
                    and co.direct_ratio > sum(o.direct_ratio*o.contract_qty) / sum(o.contract_qty)
                    and co.year_ratio > sum(o.year_ratio*o.contract_qty) / sum(o.contract_qty)
                order by co.year_ratio desc limit 0,1) better_future_symbol
    from 		operation o 
    join 		position p
    on			o.position_id = p.id
    where		o.kind = 'OPEN'
                and p.state = 'CREATED'
    group by 	o.position_id) avg_open_ratios
    on 			crtc.future_symbol = avg_open_ratios.future
    join 		future_position fp
    on			avg_open_ratios.future = fp.symbol
    left join 	current_ratios_to_open crto
    on			better_future_symbol = crto.future_symbol
    '''

historical_ratios = '''
    SELECT 	fh.open_time,
            f.symbol as future_symbol,
            fh.close as future_price,
            s.symbol as spot_symbol,
            sh.close as spot_price,
            ((fh.close / sh.close - 1) * 100) as direct_ratio,
            TIMESTAMPDIFF(HOUR, fh.open_time, f.delivery_date) + 1 as hours,
            ((fh.close / sh.close - 1) * 100) / (TIMESTAMPDIFF(HOUR, fh.open_time, f.delivery_date) + 1) as hour_ratio,
            TIMESTAMPDIFF(DAY, fh.open_time, f.delivery_date) days,
            ((fh.close / sh.close - 1) * 100) / (TIMESTAMPDIFF(hour, fh.open_time, f.delivery_date) + 1)  * 24 * 365 as year_ratio,
            f.contract_size,
            f.contract_size / fh.close as buy_per_contract,
            s.tick_size,
            s.base_asset
    FROM 	spot s
    JOIN 	spot_historical sh
    ON		s.symbol = sh.symbol
    JOIN 	future f
    ON		s.symbol = concat(f.pair, 'T')
    JOIN 	future_historical fh
    ON		f.symbol = fh.symbol
            AND sh.open_time = fh.open_time
    WHERE	f.symbol NOT LIKE '%_PERP'
    '''

operation_evaluation = '''
    select 	o.position_id,
            o.kind,
            o.future,
            o.spot,
            o.future_price,
            ft.price future_price_real,
            round((o.future_price / ft.price - 1) * 100, 4) as future_price_diff_pct,
            o.spot_price,
            st.price spot_price_real,
            round((o.spot_price / st.price - 1) * 100, 4) as spot_price_diff_pct,
            round((o.future_price / o.spot_price - 1) * 100, 4) as direct_ratio,
            round((ft.price / st.price - 1) * 100, 4) as direct_ratio_real,
            round(((o.future_price / o.spot_price) - (ft.price / st.price)) * 100, 4) as direct_ratio_diff,
            round((o.future_price / o.spot_price) / (ft.price / st.price) - 1, 4) as direct_ratio_diff_pct
    from 	operation o 
    join 	spot_order so
    on		o.id = so.operation_id
    join 	spot_trade st
    on		so.id = spot_order_id
    join 	future_order fo
    on		o.id = fo.operation_id
    join 	future_trade ft
    on 		fo.id = ft.future_order_id
    '''

def create_views():
    create_view("current_ratios_to_open", current_ratios_to_open, perp_like='%_PERP')
    create_view("current_ratios_to_close", current_ratios_to_close, perp_like='%_PERP')
    create_view("future_trade_grouped", future_trade_grouped)
    create_view("current_operations_to_open", current_operations_to_open)
    create_view("current_operations_to_close", current_operations_to_close)
    create_view("historical_ratios", historical_ratios)
    create_view("operation_evaluation", operation_evaluation)

if __name__ == '__main__':
    create_views()
