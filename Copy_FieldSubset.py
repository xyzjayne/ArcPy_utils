import arcpy

def Copy_FieldSubset(in_features, out_path, out_name, fields):
    """
    Easier function of creating a copy with a subset of fields using FeatureClassToFeatureClass_conversion.
    
    Requires unique keys in in_field and join_field.
    :param - in_table - The table or feature class to which the join table will be joined.
    :param - out_table - Output location.
    :param - fields - The subset of fields to be copied.
    """
    assert isinstance(fields, list), '"fields" needs to be a list of strings.'
    fm = arcpy.FieldMappings()
    fm.addTable(in_features)
    for field in fm.fields:
        if field.name not in fields:
            fm.removeFieldMap(fm.findFieldMapIndex(field.name))
    
    arcpy.FeatureClassToFeatureClass_conversion(in_features, out_path, out_name, field_mapping = fm)
