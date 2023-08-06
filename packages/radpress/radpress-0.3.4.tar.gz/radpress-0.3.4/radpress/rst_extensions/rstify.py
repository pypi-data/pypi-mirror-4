from radpress.readers import RstReader


def rstify(source):
    content, metadata = RstReader(source).read()
    return content
