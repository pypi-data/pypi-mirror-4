

class TagCloud(object):

    def __init__(self, urls):
        """
        cloud is a list of URLData elements we build our cloud
        from it as following:
            (tag_name, tag_count, (short_ul, url_id))
        """

        self.cloud = [(elt.url, elt.viewed, (elt.short_url, elt.id))
                      for elt in urls]

    def get_tag_cloud(self):
        """Calculate the font size of tags

        In:
          - ``urls`` -- a tuple: (url, count, data)

        Return:
          - tuples (url, count, coeff, data)
        """
        # compute tag distribution
        size_lut = dict(map(reversed, enumerate(
                            sorted(set([elt[1] for elt in self.cloud])))))

        scale = 1.0
        if len(size_lut) != 0:
            scale = 1.0 / len(size_lut)

        return [(tag, count, int(size_lut[count] * scale * 9), any_data)
                for (tag, count, any_data) in self.cloud]
