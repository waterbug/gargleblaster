# -*- coding: utf-8 -*-
"""
NASA/GSFC-specific metadata.
"""

from pangalactic.core.refdata import deds

data = []

### NOTE:  all Data Element Definitions are now in p.core.refdata

mel_deids = [
    'system_name',
    'assembly_level',
    'm_unit',
    'cold_units',
    'hot_units',
    'flight_units',
    'flight_spares',
    'etu_qual_units',
    'em_edu_prototype_units',
    'm_cbe',
    'm_ctgcy',
    'm_mev',
    'nom_p_unit_cbe',
    'nom_p_cbe',
    'nom_p_ctgcy',
    'nom_p_mev',
    'peak_p_unit_cbe',
    'peak_p_cbe',
    'peak_p_ctgcy',
    'peak_p_mev',
    'quiescent_p_cbe',
    'Vendor',
    'quoted_unit_price',
    'TRL',
    'composition',
    'additional_information',
    'similarity',
    'heritage_design',
    'heritage_mfr',
    'heritage_software',
    'heritage_provider',
    'heritage_use',
    'heritage_op_env',
    'heritage_prior_use',
    'reference_missions',
    'heritage_justification',
    'cost_structure_mass',
    'cost_electronic_complexity',
    'cost_structure_complexity',
    'cost_electronic_remaining_design',
    'cost_structure_remaining_design',
    'cost_engineering_complexity_mod_level']

gsfc_mel_deids = [d['id'] for d in deds
                  if d.get('id_ns') == 'gsfc.mel']
mel_schema = []
# use "mel_deids" for ordering of data elements in the MEL schema
for deid in mel_deids:
    if deid in gsfc_mel_deids:
        mel_schema.append(deid)

schemas = {'MEL': mel_schema}

