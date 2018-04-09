let LeafletIIIFAnnotation = {

    setOptions: function (options) {
        this.options = Object.assign({
            position: 'topright',
            draw: {
                polyline: false,
                polygon: {
                    allowIntersection: false, // Restricts shapes to simple polygons
                    drawError: {
                        color: '#e1e100', // Color the shape will turn when intersects
                        message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
                    },
                    shapeOptions: {
                        color: '#bada55'
                    }
                },
                circle: true, // Turns off this drawing tool
                rectangle: {
                    shapeOptions: {
                        clickable: false
                    }
                },
                marker: false
            },
            edit: {
                featureGroup: null, //REQUIRED!!
                remove: true
            }
        }, options)
    },

    resetMouseOverStyle: function () {
        for (e of document.getElementsByClassName("leaflet-interactive")) {
            e.style.opacity = 0;
            e.style.cursor = "pointer";
            e.onmouseover = function () { this.style.opacity = 100;};
            e.onmouseout = function () { this.style.opacity = 0; };
        }
    },

    initialize: function (map_container_id) {
        this.map = L.map(map_container_id, {
            center: [0, 0],
            crs: L.CRS.Simple,
            zoom: 5
        });
        let annoFeatures = new L.FeatureGroup();
        this.map.addLayer(annoFeatures);

        this.setOptions({edit: {featureGroup: annoFeatures}});
        this.drawControl = new L.Control.Draw(this.options);
        this.map.addControl(this.drawControl);

        this.map.on(L.Draw.Event.CREATED, function (e) {
            let type = e.layerType,
                layer = e.layer;
            annoFeatures.addLayer(layer);
        });


        /*
            Define the mouse :hover style on annotation regions
         */
        this.map.on('draw:editstart', function (e) {
            for (e of document.getElementsByClassName("leaflet-interactive")) {
                e.style.opacity = 100;
                e.style.cursor = "pointer";
                e.onmouseover = null;
                e.onmouseout = null;
            }
        });

        let resetMouseOverStyle = this.resetMouseOverStyle;
        this.map.on('draw:editstop', function (e) {
            resetMouseOverStyle();
        });

    },

    display: function display(manifest_data) {

        let page = manifest_data.sequences[0].canvases[0];
        let baseLayer = L.tileLayer.iiif(
            page.images[0].resource.service['@id'] + '/info.json'
        );
        baseLayer.addTo(this.map);

        /*
            let's draw the regions
         */
        const facsimileToolTipOptions = {direction: "center", className: "facsimileToolTip"};

        for (let id in IIIFAnnotationLoader.annotations) {
            for (let annotation of IIIFAnnotationLoader.annotations[id]) {
                let c = annotation.region.coords.split(',');
                let shape = null;
                switch (annotation.region.type) {
                    case "rect":
                        shape = L.rectangle([this.map.unproject([c[0], c[1]], 2), this.map.unproject([c[2], c[3]], 2)]);
                        break;
                    case "polygon":
                        let pointList = [];
                        for (let i = 0; i < c.length; i += 2) {
                            pointList.push(this.map.unproject([c[i], c[i + 1]], 2));
                        }
                        shape = L.polygon(pointList);
                        break;
                    case "circle":
                        shape = L.circle(this.map.unproject([c[0], c[1]], 2), {radius: c[2] * 0.33});
                        break;
                }
                this.options.edit.featureGroup.addLayer(shape);
                shape.bindTooltip(annotation.content, facsimileToolTipOptions);
                shape.addTo(this.map);
            }
        }

        this.resetMouseOverStyle();
    }
};
