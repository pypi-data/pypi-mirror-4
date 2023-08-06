from cubicweb.web.formfields import normalize_filename

rset = rql(r'Any F, N WHERE F is IN (File, Image), F data_name N')
for _file in rset.entities():
    old_filename = _file.data_name
    new_filename = normalize_filename(old_filename)
    if old_filename != new_filename:
        _file.set_attributes(data_name=new_filename)
commit()
