from __future__ import annotations
from typing import List, Dict, Any
from config import MAX_ITEM_COUNT

ROLE_MAP = {
    "top": "TOP",
    "jungle": "JNG",
    "middle": "MID",
    "mid": "MID",
    "bottom": "ADC",
    "adc": "ADC",
    "utility": "SUP",
    "support": "SUP",
    "none": "UNK",
    "unknown": "UNK"
}

def _clean_item_name(name: str) -> str:
    # keep short; remove commas to avoid token spill
    s = str(name).replace(',', '')
    if len(s) > 20:
        s = s[:17] + '…'
    return s

def summarize_allgamedata(api: Dict[str, Any]) -> str:
    """Returns a compact, model-friendly snapshot string.
    Accepts the raw response of /liveclientdata/allgamedata.
    Keeps <= 1–2k tokens even late game.
    """
    if not api:
        return "NO_GAME"

    gtime = int(api.get('gameData', {}).get('gameTime', 0))
    # separate teams if available
    players = api.get('allPlayers', [])
    blue, red = [], []
    for p in players:
        team = p.get('team', '').upper()
        (blue if team == 'ORDER' else red).append(p)

    def line(p: Dict[str, Any]) -> str:
        role = ROLE_MAP.get(str(p.get('position','unknown')).lower(), 'UNK')
        champ = p.get('championName', '???')
        lvl = p.get('level', 0)
        dead = p.get('isDead', False)
        k = p.get('scores', {}).get('kills', 0)
        d = p.get('scores', {}).get('deaths', 0)
        a = p.get('scores', {}).get('assists', 0)
        items = [ _clean_item_name(i.get('displayName', i.get('itemID',''))) for i in p.get('items', []) ]
        if len(items) > MAX_ITEM_COUNT: items = items[:MAX_ITEM_COUNT]
        death = ' DEAD' if dead else ''
        return f"{role:<3} {champ:<14} L{lvl:<2} {k}/{d}/{a}{death} | {'|'.join(items)}"

    def block(team_list: List[Dict[str, Any]]) -> str:
        # try to sort by inferred role order to reduce churn
        order = {'TOP':0,'JNG':1,'MID':2,'ADC':3,'SUP':4}
        team_list_sorted = sorted(team_list, key=lambda p: order.get(ROLE_MAP.get(str(p.get('position','unknown')).lower(),'UNK'), 9))
        return "\n".join(line(p) for p in team_list_sorted)

    blue_block = block(blue) if blue else ''
    red_block  = block(red) if red else ''

    # Keep stable section headers so the model can parse reliably
    out = [
        f"TIME {gtime}s",
        "BLUE:",
        blue_block or "(unknown)",
        "RED:",
        red_block or "(unknown)",
    ]
    return "\n".join(out).strip()
