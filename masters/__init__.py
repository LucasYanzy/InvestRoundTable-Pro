"""masters — 31位大师分析模块

公共 API:
    create_stage1_masters()  → List[InvestmentMaster]   (14 位)
    create_stage2_masters()  → List[TechnicalMaster]    (12 位)
    create_stage3_masters()  → List[SignalMaster]       (11 位)
"""

from masters.investment_master import create_stage1_masters, InvestmentMaster
from masters.technical_master import create_stage2_masters, TechnicalMaster, build_indicator_snapshot
from masters.signal_master import create_stage3_masters, SignalMaster
from masters.base_master import BaseMaster, MasterOpinion

__all__ = [
    "create_stage1_masters",
    "create_stage2_masters",
    "create_stage3_masters",
    "build_indicator_snapshot",
    "BaseMaster",
    "MasterOpinion",
    "InvestmentMaster",
    "TechnicalMaster",
    "SignalMaster",
]
