def extract_urls(data):
    urls = []

    def recursive_extract(item):
        if isinstance(item, dict):
            if 'url' in item:
                urls.append(item['chunkSource'].replace('link://', ''))
            for value in item.values():
                recursive_extract(value)
        elif isinstance(item, list):
            for element in item:
                recursive_extract(element)

    recursive_extract(data)
    return urls
