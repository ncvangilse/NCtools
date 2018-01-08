# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 16:10:53 2016

@author: fbx182
"""

from NCs_tools import fdb_utils


class Jupiter(fdb_utils.Fdb_connection):
    def __init__(self, fnam):
        fdb_utils.Fdb_connection.__init__(self, fnam)

    def make_code_view(self,vName, ctShorttext):
        """Return a string  that can be sent to the firebird server to create a view 
        that holds human readable conversions between CODE.CODE and CODE.SHORTTEXT for a given description (CODETYPE.SHORTTEXT)
        Note: The ctShortext must be a list or tuple!"""
        ctShorttext = self.list_to_str(ctShorttext)
        s = (
               'CREATE VIEW {} '
               'AS '
               'SELECT CODE.CODE, CODE.SHORTTEXT '
               'FROM (CODE JOIN CODETYPE ON  CODE.CODETYPE = CODETYPE.CODETYPE) '
                'WHERE CODETYPE.SHORTTEXT IN  {} '
               ).format(vName, ctShorttext)
        return s
    
    def make_code_score(self,src, criteria, tgt, v=None):
        """Return a string  that can be sent to the firebird server to update score fields
        src is the source string formatted as a string containing a table.field
        If v is given (optional) as a name of a field in a view, it is interpreted to be a 
        translating view between the source field and the criteria.
        criteria is a dict containg one ore more keys describing the criteria and the fields describe the resulting score
        tgt is the target string formatted as a string containing a table.field"""
        Src, fSrc = src.split('.')
        Tgt, fTgt = tgt.split('.')
        if v:
            V, fV = v.split('.')
            using = 'USING ({Src} a join {V} c ON a.{fSrc}=c.CODE) '
        else:
            V = fV = None
            using = 'USING {Src} a '
        cases = ''
        for crit, val in criteria.items():
            if v:
                cases += 'WHEN c.{fV} {crit} THEN {val} '.format(crit=crit, val=val, fV=fV)
            else:
                cases += 'WHEN a.{fSrc} {crit} THEN {val} '.format(crit=crit, val=val, fSrc=fSrc)
        s = (
             'MERGE INTO {Tgt} '
             + using +
             'ON ({Tgt}.BOREHOLENO = a.BOREHOLENO) '
             'WHEN MATCHED THEN '
             'UPDATE SET {fTgt} = CASE '
             + cases +
             'ELSE 0 '
             'END '
             ).format(Src=Src, fSrc=fSrc, Tgt=Tgt, fTgt=fTgt, V=V,fV=fV)
        return s  
    
    def init_geoscene(self):
        create_geoscene = (
                            'CREATE VIEW GEOSCENE AS '
                            'SELECT a.BOREHOLENO, a.DRILLDEPTH, a.XUTM, a.YUTM, a.ELEVATION, b.SCORE_TOTAL, c.ROCKSYMBOL, c.CLAYINDEX, c.TOP, c.BOTTOM '
                            'FROM BOREHOLE a join (BOREHOLE_RATING b JOIN LITHSAMP c ON b.BOREHOLENO=c.BOREHOLENO) ON a.BOREHOLENO = b.BOREHOLENO '
                           )
        self.run(create_geoscene)
        
        
