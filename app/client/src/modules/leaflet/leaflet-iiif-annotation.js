const LeafletIIIFAnnotation = {

    ZOOM: 2,

    resetMouseOverStyle: function () {
        for (let e of document.getElementsByClassName("leaflet-interactive")) {
            e.style.opacity = 0;
            e.style.cursor = "pointer";
            e.onmouseover = function () {
                this.style.opacity = 100;
            };
            e.onmouseout = function () {
                this.style.opacity = 0;
            };
        }
    },
    showShapes: function () {
        for (let e of document.getElementsByClassName("leaflet-interactive")) {
            e.style.opacity = 100;
            e.style.cursor = "pointer";
            e.onmouseover = null;
            e.onmouseout = null;
        }
    },
    initialize: function (leaflet_map, featureGroup) {

        this.annotations = [];
        this.annotationTypes = {};
        this.map = leaflet_map;
        this.featureGroup = featureGroup;
    },

    _makeAnnotation: function (layer) {
        const tooltip = layer.getTooltip();
        const content = tooltip === undefined ? "" : tooltip.getContent();
        let coords = [];
        if (layer instanceof L.Circle) {
            const c = layer.toGeoJSON().geometry.coordinates;
            const center = this.map.project([c[1], c[0]], LeafletIIIFAnnotation.ZOOM);
            coords = [center.x, center.y, layer.getRadius()]
        } else {
            // todo instance of L.Rectangle
            // else polygon
            for (let c of layer.toGeoJSON().geometry.coordinates) {
                for (let i = 0; i < c.length; i++) {
                    const point = this.map.project([c[i][1], c[i][0]], LeafletIIIFAnnotation.ZOOM);
                    coords.push(point.x + "," + point.y);
                }
            }
        }

        if (!layer.annotation_type) {
            layer.annotation_type = this.annotationTypes["transcription"];
        }

        return {
            region: {coords: coords.join(',')},
            content: content,
            annotation_type: layer.annotation_type
        };
    },

    getAnnotations: function () {
        this.annotations = [];
        const _this = this;
        this.featureGroup.eachLayer(function (layer) {
            _this.annotations.push(_this._makeAnnotation(layer))
        });
        return this.annotations
    },

    setAnnotations: function (annotationLists) {
        this.featureGroup.clearLayers();
        /*
            let's draw the regions
         */
        console.log(this.featureGroup.getLayers().length);

        const facsimileToolTipOptions = {direction: "center", className: "facsimileToolTip"};

        for (let listId in annotationLists) {
            for (let annotation of annotationLists[listId].annotations) {

                let c = annotation.region.coords.split(',');
                let shape = null;
                switch (annotation.region.type) {
                    case "rect":
                        shape = L.rectangle([this.map.unproject([c[0], c[1]], LeafletIIIFAnnotation.ZOOM), this.map.unproject([c[2], c[3]], 2)]);
                        break;
                    case "polygon":
                        let pointList = [];
                        for (let i = 0; i < c.length; i += 2) {
                            pointList.push(this.map.unproject([c[i], c[i + 1]], LeafletIIIFAnnotation.ZOOM));
                        }
                        shape = L.polygon(pointList);
                        break;
                    case "circle":
                        shape = L.circle(this.map.unproject([c[0], c[1]], LeafletIIIFAnnotation.ZOOM), {radius: c[2] * 0.25});
                        break;
                }
                //add the shape & the content to the map

                shape.bindTooltip(annotation.content, facsimileToolTipOptions);
                shape.annotation_type = annotationLists[listId].annotation_type;
                this.featureGroup.addLayer(shape);
                this.annotationTypes[annotationLists[listId].annotation_type.label] = annotationLists[listId].annotation_type;
                shape.addTo(this.map);
            }
        }
        console.log(this.featureGroup.getLayers().length);
        this.resetMouseOverStyle();
    }
};

export default LeafletIIIFAnnotation;
