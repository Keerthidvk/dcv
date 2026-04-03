def is_supported_file(filepath, supported_types):
    return filepath.lower().endswith(supported_types)


def safe_get(dictionary, key, default=None):
    return dictionary.get(key, default)


def normalize_identifier(name):
    return name.strip().lower()
