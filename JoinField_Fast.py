import arcpy

def JoinField_Fast(in_table, in_field, join_table, join_field, fields= '*'):
    """Alternative to arcpy's own JoinField.
    Populates new fields in in_data with dictionaries of key-value pairs from join_table.
    Reference: 
    https://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-data-access/searchcursor-class.htm
    https://gis.stackexchange.com/questions/95957/most-efficient-method-to-join-multiple-fields-in-arcgis
    
    Requires unique keys in in_field and join_field.
    :param - in_table - The table or feature class to which the join table will be joined.
    :param - in_field - The field in the input table on which the join will be based.
    :param - join_table - The table to be joined to the input table.
    :param - join_field - The field in the join table that contains the values on which the join will be based.
    :param - fields - optional. The fields from the join table to be included in the join.
    """
    
    in_field_values = [x[0] for x in arcpy.da.TableToNumPyArray(in_table, in_field)]
    join_field_values = [x[0] for x in arcpy.da.TableToNumPyArray(join_table, join_field)]

    
    if fields == '*':
        field_list = [field.name for field in arcpy.ListFields(join_table) if field.name != join_field]
    else: field_list = fields
    
    # make sure field doesn't already exist in in_table
    in_table_fields = [field.name for field in arcpy.ListFields(in_table)]
    field_list_final = []
    for field in field_list:
        if field in in_table_fields:
            field_list_final.append(field + '_1')
        else:
            field_list_final.append(field)
    
    field_type_dict = dict(zip([field.name for field in arcpy.ListFields(join_table)],
        [field.type for field in arcpy.ListFields(join_table)]))
        
    join_value_dict = {}
    with arcpy.da.SearchCursor(join_table, [join_field] + field_list) as rows:
        for row in rows:
            join_key = row[0]
            join_value_dict[join_key] = row[1:]
            
    for field_final, field in zip(field_list_final, field_list):
        arcpy.AddField_management(in_table, field_final, field_type_dict[field])
        
    with arcpy.da.UpdateCursor(in_table,  [in_field] + field_list_final) as recs:
        for rec in recs:
            join_key = rec[0]
            if join_value_dict.has_key(join_key):
                # Replace null values with 0 or empty string
                values = list(join_value_dict[join_key])
                if None in values:
                    for index, val in enumerate(values):
                        if field_type_dict[field_list[index]] == 'String':
                            values[index] = str(val or '')
                        elif field_type_dict[field_list[index]] == 'Double':
                            values[index] = float(val or 0)
                        elif field_type_dict[field_list[index]] == 'Integer':
                            values[index] = int(val or 0)
                
            else:
                values = []
                for index in range(len(rec[1:])):
                    if field_type_dict[field_list[index]] == 'String':
                        values.append( str(val or ''))
                    elif field_type_dict[field_list[index]] == 'Double':
                        values.append( float(val or 0))
                    elif field_type_dict[field_list[index]] == 'Integer':
                        values.append( int(val or 0))
                    else:
                        values.append(0)
            rec[1:] = tuple(values)
            recs.updateRow(rec)
