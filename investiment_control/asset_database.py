from dataclasses import dataclass

@dataclass
class AssetInfo:
    name:str
    ticker:str
    asset_class:str
    stock_b3:bool=False
    stock_us:bool=False
    bond:bool=False

DICT_ASSET_INFO = { 
'CSMG3':AssetInfo(name="CSMG", ticker="CSMG3.SA", asset_class="Ação", stock_b3=True),
'RAIZ4':AssetInfo(name="RAIZ", ticker="RAIZ4.SA", asset_class="Ação", stock_b3=True),
'SLCE3':AssetInfo(name="SLCE", ticker="SLCE3.SA", asset_class="Ação", stock_b3=True),
'SUZB3':AssetInfo(name="SUZB", ticker="SUZB3.SA", asset_class="Ação", stock_b3=True),
'BBAS3':AssetInfo(name="BBAS", ticker="BBAS3.SA", asset_class="Ação", stock_b3=True),
'ROMI3':AssetInfo(name="ROMI", ticker="ROMI3.SA", asset_class="Ação", stock_b3=True),
'ITSA4':AssetInfo(name="ITSA", ticker="ITSA4.SA", asset_class="Ação", stock_b3=True),
'CMIG4':AssetInfo(name="CMIG", ticker="CMIG4.SA", asset_class="Ação", stock_b3=True),
'GGBR4':AssetInfo(name="GGBR", ticker="GGBR4.SA", asset_class="Ação", stock_b3=True),
'BBDC4':AssetInfo(name="BBDC", ticker="BBDC4.SA", asset_class="Ação", stock_b3=True),
'VALE3':AssetInfo(name="VALE", ticker="VALE3.SA", asset_class="Ação", stock_b3=True),
'TRPL4':AssetInfo(name="TRPL", ticker="ISAE4.SA", asset_class="Ação", stock_b3=True),
'CIEL3':AssetInfo(name="CIEL", ticker="CIEL3.SA", asset_class="Ação", stock_b3=True),
'SAPR4':AssetInfo(name="SAPR", ticker="SAPR4.SA", asset_class="Ação", stock_b3=True),
'PSSA3':AssetInfo(name="PSSA", ticker="PSSA3.SA", asset_class="Ação", stock_b3=True),
'PVBI11':AssetInfo(name="PVBI", ticker="PVBI11.SA",asset_class="FII", stock_b3=True),
'HSLG11':AssetInfo(name="HSLG", ticker="HSLG11.SA",asset_class="FII", stock_b3=True),
'ALZR11':AssetInfo(name="ALZR", ticker="ALZR11.SA",asset_class="FII", stock_b3=True),
'HGRU11':AssetInfo(name="HGRU", ticker="HGRU11.SA",asset_class="FII", stock_b3=True),
'HSML11':AssetInfo(name="HSML", ticker="HSML11.SA",asset_class="FII", stock_b3=True),
'HGPO11':AssetInfo(name="HGPO", ticker="HGPO11.SA",asset_class="FII", stock_b3=True),
'HGLG11':AssetInfo(name="HGLG", ticker="HGLG11.SA",asset_class="FII", stock_b3=True),
'BODB11':AssetInfo(name="BODB", ticker="BODB11.SA",asset_class="FII", stock_b3=True),
'TRXF11':AssetInfo(name="TRXF", ticker="TRXF11.SA",asset_class="FII", stock_b3=True),
'CLIN11':AssetInfo(name="CLIN", ticker="CLIN11.SA",asset_class="FII", stock_b3=True),
'CPTI11':AssetInfo(name="CPTI", ticker="CPTI11.SA",asset_class="FII", stock_b3=True),
'KNSC11':AssetInfo(name="KNSC", ticker="KNSC11.SA",asset_class="FII", stock_b3=True),
'KNIP11':AssetInfo(name="KNIP", ticker="KNIP11.SA",asset_class="FII", stock_b3=True),
'RBRR11':AssetInfo(name="RBRR", ticker="RBRR11.SA",asset_class="FII", stock_b3=True),
'ALUG11':AssetInfo(name="ALUG", ticker="ALUG11.SA",asset_class="USD", stock_b3=True),
'KORE11':AssetInfo(name="KORE", ticker="KORE11.SA",asset_class="FII", stock_b3=True),
'KNRI11':AssetInfo(name="KNRI", ticker="KNRI11.SA",asset_class="FII", stock_b3=True),
'JURO11':AssetInfo(name="JURO", ticker="JURO11.SA",asset_class="FII", stock_b3=True),
'PATL11':AssetInfo(name="PATL", ticker="PATL11.SA",asset_class="FII", stock_b3=True),
'HGRE11':AssetInfo(name="HGRE", ticker="HGRE11.SA",asset_class="FII", stock_b3=True),
'RBVA11':AssetInfo(name="RBVA", ticker="RBVA11.SA",asset_class="FII", stock_b3=True),
'KNCA11':AssetInfo(name="KNCA", ticker="KNCA11.SA",asset_class="FII", stock_b3=True),
'BTCI11':AssetInfo(name="BTCR", ticker="BTCI11.SA",asset_class="FII", stock_b3=True),
'JSRE11':AssetInfo(name="JSRE", ticker="JSRE11.SA",asset_class="FII", stock_b3=True),
'CVBI11':AssetInfo(name="CVBI", ticker="CVBI11.SA",asset_class="FII", stock_b3=True),
'BCRI11':AssetInfo(name="BCRI", ticker="BCRI11.SA",asset_class="FII", stock_b3=True),
'GGRC11':AssetInfo(name="GGRC", ticker="GGRC11.SA",asset_class="FII", stock_b3=True),
'HGCR11':AssetInfo(name="HGCR", ticker="HGCR11.SA",asset_class="FII", stock_b3=True),
'KNCR11':AssetInfo(name="KNCR", ticker="KNCR11.SA",asset_class="FII", stock_b3=True),
'ICRI11':AssetInfo(name="ICRI", ticker="ICRI11.SA",asset_class="FII", stock_b3=True),
'AFHI11':AssetInfo(name="AFHI", ticker="AFHI11.SA",asset_class="FII", stock_b3=True),
'SPXI11':AssetInfo(name="SPXI", ticker="SPXI11.SA",asset_class="USD", stock_b3=True),
'BITH11':AssetInfo(name="BITH", ticker="BITH11.SA",asset_class="USD", stock_b3=True),
'USDB11':AssetInfo(name="USDB", ticker="USDB11.SA",asset_class="USD", stock_b3=True),
'LFTS11':AssetInfo(name="LFTS", ticker="LFTS11.SA",asset_class="Tesouro",stock_b3=True),
'Selic 2026':AssetInfo(name="Selic 2026", ticker="Selic 2026", asset_class="Tesouro", bond=True),
'Selic 2029':AssetInfo(name="Selic 2029", ticker="Selic 2029", asset_class="Tesouro", bond=True),
'IPCA+ 2029':AssetInfo(name="IPCA+ 2029", ticker="IPCA+ 2029", asset_class="Tesouro", bond=True),
'IPCA+ 2045':AssetInfo(name="IPCA+ 2045", ticker="IPCA+ 2045", asset_class="Tesouro", bond=True),
'IPCA+ 2050':AssetInfo(name="IPCA+ 2050", ticker="IPCA+ 2050", asset_class="Tesouro", bond=True),
'Prefixado 2029':AssetInfo(name="Pref 2029", ticker="Prefixado 2029",asset_class="Tesouro", bond=True),
'BIL':AssetInfo(name="BIL", ticker="BIL", asset_class="USD", stock_us=True),
'IBIT':AssetInfo(name="IBIT", ticker="IBIT", asset_class="USD", stock_us=True),
'TLT':AssetInfo(name="TLT", ticker="TLT", asset_class="USD", stock_us=True),
'SHY':AssetInfo(name="SHY", ticker="SHY", asset_class="USD", stock_us=True),
'IVV':AssetInfo(name="IVV", ticker="IVV", asset_class="USD", stock_us=True),
}

ticker=["ITSA4","RAIZ4","BBAS3","CSMG3","ICRI11","HGRE11"],


ticker=["Selic 2029","TRXF11","HGLG11","ALZR11","KNSC11","HSML11","HGRU11","KNIP11","HGRE11","ICRI11"],
