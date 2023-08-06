if not 'Image' in schema:
    add_entity_type('Image')
else:
    set_size_constraint('Image', 'data_encoding', 20)
set_size_constraint('File', 'data_encoding', 20)
