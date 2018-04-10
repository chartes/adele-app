
const LeafletIIIFAnnotation = {

    resetMouseOverStyle: function () {
        for (let e of document.getElementsByClassName("leaflet-interactive")) {
            e.style.opacity = 0;
            e.style.cursor = "pointer";
            e.onmouseover = function () { this.style.opacity = 100;};
            e.onmouseout = function () { this.style.opacity = 0; };
        }
    },

    initialize: function (leaflet_map) {

        this.map = leaflet_map;

        /*
            Define the mouse :hover style on annotation regions
         */
        this.map.on('draw:editstart', function (e) {
            for (let e of document.getElementsByClassName("leaflet-interactive")) {
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

    display: function display(featureGroup, annotations) {

        /*
            let's draw the regions
         */
        const facsimileToolTipOptions = {direction: "center", className: "facsimileToolTip"};

        for (let id in annotations) {
            for (let annotation of annotations[id]) {
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
                featureGroup.addLayer(shape);
                shape.bindTooltip(annotation.content, facsimileToolTipOptions);
                shape.addTo(this.map);
            }
        }

        this.resetMouseOverStyle();
    }
};

export default LeafletIIIFAnnotation;
