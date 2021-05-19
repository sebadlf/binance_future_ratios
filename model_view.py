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


current_ratios = '''
    SELECT 	f.symbol as future_symbol,
            fp.mark_price as future_price,
            s.symbol as spot_symbol,
            sp.price as spot_price,
            ((fp.mark_price / sp.price - 1) * 100) as direct_ratio,
            TIMESTAMPDIFF(HOUR, now(), f.delivery_date) + 1 as hours,
            ((fp.mark_price / sp.price - 1) * 100) / (TIMESTAMPDIFF(HOUR, now(), f.delivery_date) + 1) as hour_ratio,
            TIMESTAMPDIFF(DAY, now(), f.delivery_date) days,
            ((fp.mark_price / sp.price - 1) * 100) / (TIMESTAMPDIFF(hour, now(), f.delivery_date) + 1)  * 24 * 365 as year_ratio,
            f.contract_size,
            f.contract_size / fp.mark_price as buy_per_contract,
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

create_view("current_ratios", current_ratios, perp_like='%_PERP')

current_operation_to_close = '''
    SELECT 	p.id as position_id,
            o.id as operation_id,
            cr.*,
            p.contract_qty, 		
            t.amount as transfer_amount,
            ft.base_qty as future_base_qty,
            ft.commission as future_commission,            
            o.direct_ratio - cr.direct_ratio as direct_ratio_diff,
            o.year_ratio - cr.year_ratio as year_ratio_diff,
            ocr.future_symbol as better_future_symbol
    FROM	position p	
    JOIN 	operation o
    ON		p.id = o.position_id
            AND p.state = 'CREATED'
    JOIN 	transfer t
    ON		o.id = t.operation_id
    JOIN	future_order fo
    ON		o.id = fo.operation_id
    JOIN	future_trade ft
    ON		fo.id = ft.future_order_id
    JOIN	current_ratios cr
    ON		o.future = cr.future_symbol
            AND o.spot = cr.spot_symbol
    LEFT JOIN	current_ratios ocr
    ON		ocr.direct_ratio - o.direct_ratio > 0
            AND ocr.year_ratio - o.year_ratio > 0   
    '''

create_view("current_operation_to_close", current_operation_to_close)

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

create_view("historical_ratios", historical_ratios)
