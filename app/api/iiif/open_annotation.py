

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


def make_specific_rectangular_resource(manifest_url, canvas_url, img, rect_coords):
    """

    :param canvas_url:
    :param manifest_url:
    :param img:
    :param rect_coords:
    :return:
    """
    img_full = img["resource"]["@id"]
    img_service_id = img["resource"]["service"]["@id"]

    left_part = img_full[0:img_full.rindex("/full/full")+1]
    right_part = img_full[img_full.rindex("/full"):]
    img_rect_uri = left_part + rect_coords + right_part

    res = {
        "@id": img_rect_uri,
        "@type": "oa:SpecificResource",
        "within": {
            "@id": manifest_url,
            "@type": "sc:Manifest"
        },
        "full": {
            "@id": img_full,
            "@type": "dctypes:Image",
            "service": {
                "@context": "http://iiif.io/api/image/2/context.json",
                "@id": img_service_id,
                "profile": "http://iiif.io/api/image/2/level2.json"
            }
        },
        "selector": {
            "@context": "http://iiif.io/api/annex/openannotation/context.json",
            "@type": "iiif:ImageApiSelector",
            "region": rect_coords
        },
        "on": canvas_url
    }

    return res


def make_specific_svg_resource(manifest_url, canvas_url, img, fragment_coords):
    """

    :param canvas_url:
    :param manifest_url:
    :param img:
    :param fragment_coords:
    :return:
    """
    img_service_id = img["resource"]["service"]["@id"]
    img_full = img["resource"]["@id"]

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

    res = {
        "@type": "oa:SpecificResource",
        "within": {
            "@id": manifest_url,
            "@type": "sc:Manifest"
        },
        "full": {
          "@id": img_full,
          "@type": "dctypes:Image"
        },
        "selector": {
          "@type":["oa:SvgSelector","cnt:ContentAsText"],
          "chars": svg_data
        },
        "on": canvas_url
    }

    return res


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
        specific_resource = make_specific_rectangular_resource(manifest_url, canvas_url, img, fragment_coords)
    else:
        specific_resource = make_specific_svg_resource(manifest_url, canvas_url, img, fragment_coords)

    anno = {
        "@type": "oa:Annotation",
        "motivation": "sc:painting",
        "resource": {
            "@type": "cnt:ContentAsText",
            "chars": content,
            "format": format,
            "metadata": metadata
        },
        "on": specific_resource
    }
    if res_uri is not None:
        anno["resource"]["@id"] = res_uri

    return anno


if __name__ == "__main__":
    pass
