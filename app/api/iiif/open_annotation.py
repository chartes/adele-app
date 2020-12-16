import math


def make_annotation_layer(url, annotation_lists, motivation):
    return {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": url,
        "@type": "sc:Layer",
        "label": motivation,
        "otherContent": annotation_lists
    }


def make_annotation_list(url, annotations):
    """

    :param annotation_type:
    :param doc_id:
    :param annotations:
    :return:
    """
    return {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": url,
        "@type": "sc:AnnotationList",
        "resources": annotations,
        "metadata": [

        ],
    }


def make_specific_rectangular_selector(rect_coords):
    """

    :param canvas_url:
    :param manifest_url:
    :param img:
    :param rect_coords:
    :return:
    """
    x,y,w,h = rect_coords.split(',')

    return {
        "@type": "oa:FragmentSelector",
        "value": "xywh=" + ','.join([x, y, str(math.ceil(int(w)/2)), str(math.ceil(int(h)/2))])
    }


def make_specific_svg_selector(manifest_url, canvas_url, img, fragment_coords):
    """

    :param canvas_url:
    :param manifest_url:
    :param img:
    :param fragment_coords:
    :return:
    """
    coords = fragment_coords.split(",")

    if len(coords) == 3:
        fig_path = "<circle cx='{0}' cy='{1}' r='{2}'/>".format(*coords)
    else:
        # move to coords
        M = "M {0} {1}".format(*coords)
        # line to coords
        Ls = ""
        for i, c in enumerate(coords[2:]):
            if i % 2 == 0:
                Ls += "L "
            Ls += c + " "
        Ls = Ls.rstrip()
        fig_path = "<path xmlns='http://www.w3.org/2000/svg' d='{0} {1} z'/>".format(M, Ls)

    svg_data = "<svg xmlns='http://www.w3.org/2000/svg'>{0}</svg>".format(fig_path)

    return {
        "@type": "oa:SvgSelector",
        "value": svg_data
    }

def make_annotation(manifest_url, canvas_url, img, fragment_coords, res_uri, content, metadata=None, format="text/html"):
    """

    :param metadata:
    :param canvas_url:
    :param manifest_url:
    :param img:
    :param fragment_coords:
    :param res_uri:
    :param content:
    :param format:
    :return:
    """
    if metadata is None:
        metadata = {}
    if len(fragment_coords.split(",")) == 4:
        selector = make_specific_rectangular_selector(fragment_coords)
    else:
        #TODO ? ne semble pas fonctionner avec Mirador 3
        #return {}
        selector = make_specific_svg_selector(manifest_url, canvas_url, img, fragment_coords)

    anno = {
        "@type": "oa:Annotation",
        "motivation": "sc:painting",
        "resource": {
            "@type": "dctypes:Text",
            "chars": content
        },
        "on": {
            "@type": "oa:SpecificResource",
            "within": {
                "@id": manifest_url,
                "@type": "sc:Manifest"
            },
            "selector": selector,
            "full": canvas_url
        }
    }
    if res_uri is not None:
        anno["resource"]["@id"] = res_uri

    return anno


if __name__ == "__main__":
    pass
