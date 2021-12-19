
def to_json(obj):
    return str(obj) \
        .replace("'", "\"") \
        .replace("True", "true") \
        .replace("False", "false") \
        .replace("None", "n/a")
