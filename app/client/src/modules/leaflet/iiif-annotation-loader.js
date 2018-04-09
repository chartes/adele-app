/*
 * IIIFAnnotationLoader 1.0
 * Compatible with IIIF Presentation API 2.1
 *
 * Extract "otherContent" annotations:
 * Filter on type oa:Annotation and motivation sc:painting
 * Look at embeded content in the resource of type cnt:ContentAsText
 * Then look at the resource type on the "on" attribute of the annotation
 * and figure out which kind of geometrical representations it conveys:
 * - xywh= coords (rect)
 * - iiif:ImageApiSelector (rect)
 * - oa:SpecificResource (a rect or a figure [path, circle] in a <SVG>)
 * - a mix of them
 *
 *
 * author : Julien Pilla
 */

let IIIFAnnotationLoader = {
    options: {},

    initialize: function (manifest_data, options = {}) {
        this.manifest = manifest_data;
        this.options = Object.assign(this.options, options);
        this.annotations = [];

        let canvas = this.getFirstCanvas();
        // get annotation lists urls
        let axiosPromises = [];
        for (let oc of canvas.otherContent) {
            if (oc["@type"] === "sc:AnnotationList") {
                axiosPromises.push(this.loadAnnotationList(oc["@id"]));
            }
        }
        return axios.all(axiosPromises);
    },
    getFirstCanvas: function () {
        //TODO: gérer erreurs
        return this.manifest.sequences[0].canvases[0];
    },

    _getSelectorRegion: function (selector, selector_type) {
        let region = null;
        // case 2
        if (selector_type === "iiif:ImageApiSelector") {
            region = {coords: selector.region, type: "rect"}
        // case 3
        } else if (selector_type === "oa:SvgSelector") {
            let dom = new window.DOMParser();
            let svg = dom.parseFromString(selector.chars, "text/xml");
            let s = selector.chars;
            if (s.indexOf("circle") !== -1) {
                let circle = svg.getElementsByTagName("circle")[0];
                let coords = [
                    circle.cx.baseVal.valueAsString,
                    circle.cy.baseVal.valueAsString,
                    circle.r.baseVal.valueAsString
                ];
                region = {coords: coords.join(","), type: "circle"}
            } else if (s.indexOf("path") !== -1) {
                // Only support path containing polylines : M x x L x x L x x ...
                // let's parse the svg <path> element
                // substr to get path coords from the svg string
                let p = s.substr(s.indexOf(" d='"), s.length);
                p = p.substr(4, p.indexOf('z') - 5);
                // need to parse M and L
                let t = p.split("L");
                t[0] = t[0].split("M")[1]; // first coord
                t[t.length-1] = t[t.length-1].split("z")[0]; // last coord
                let coords = [];
                for (let i in t) {
                    let x_y = t[i].trim().split(" ");
                    coords.push(x_y[0]);
                    coords.push(x_y[1]);
                }
                region = {coords: coords.join(","), type: "polygon"}
            }

        }
        return region
    }
    ,
    parseAnnotation: function (annotation) {
        //console.log("Adding resource " + annotation.resource["@id"]);
        let new_annotation = null;
        if (annotation["@type"] === "oa:Annotation" && annotation["motivation"] === "sc:painting") {
            new_annotation = {
                "id": annotation.resource["@id"]
            };
            //get the textual content
            if (annotation.resource["@type"] === "cnt:ContentAsText") {
                new_annotation = Object.assign(new_annotation, {
                    content: annotation.resource.chars,
                    format: annotation.resource.format
                });
            }
            /*
                get the fragment coords
                cases :
                1) simple rect xywh=
                2) complexe IIIF rect : oa:SpecificResource
                3) SVG element  : oa:SpecificResource
                4) ??
             */
            var region = null;
            if (annotation.on["@type"] === "oa:SpecificResource") {
                if (annotation.on.selector) {
                    // assume that if it's a string then it's a single value
                    if (typeof annotation.on.selector["@type"] === 'string') {
                        region = this._getSelectorRegion(annotation.on.selector, annotation.on.selector["@type"]);
                    } else {
                        // assume that @type is a list
                        region = [];
                        for (let selector_type of annotation.on.selector["@type"]) {
                            let new_region = this._getSelectorRegion(annotation.on.selector, selector_type);
                            if (new_region) {
                                region.push(new_region);
                            }
                        }
                    }
                }
            }
            else if (typeof annotation.on === "string" && annotation.on.indexOf("xywh=") !== 0) {
                // case 1
                let i = annotation.on.indexOf("xywh=");
                region = {coords: annotation.on.substr(i+5, annotation.on.length), type: "rect"}
            }

            // dont add coords if there is none
            if (region) {
                if (Array.isArray(region) && region.length === 1) {
                    region = region[0];
                }
                new_annotation = Object.assign(new_annotation, {
                    region: region
                });
            }

        }
        return new_annotation;
    },


    loadAnnotationList: function (list_url) {
        //console.log("Adding list " + list_url);
        if (!this.annotations[list_url])
            this.annotations[list_url] = [];

        return axios.get(list_url)
            .then(response => {
                for (let annotation of response.data.resources) {
                    let new_annotation = this.parseAnnotation(annotation);
                    if (new_annotation) {
                        this.annotations[list_url].push(new_annotation);
                    }
                }
            })
            .catch(error => {
                console.log(error)
            });
    }
};