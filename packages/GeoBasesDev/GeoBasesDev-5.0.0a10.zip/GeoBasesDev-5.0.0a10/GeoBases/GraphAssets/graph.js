
if (!String.fmt) {
    String.prototype.fmt = function() {
        var formatted = this;
        var i;
        for (i=0; i<arguments.length; i++) {
            var regexp = new RegExp('\\{'+i+'\\}', 'gi');
            formatted = formatted.replace(regexp, arguments[i]);
        }
        return formatted;
    };
}


function overflow(text) {

    if (typeof text !== "string") {
        return text;
    }

    if (text.length < 30) {
        return text;
    }

    return ('' + text).slice(0, 25) + '...';

}




function initialize(jsonData) {

    var graph_fields = jsonData.meta.graph_fields;
    var graph_weight = jsonData.meta.graph_weight;

    $('#fields').html('for <i>{0}</i> (<i>{1}</i> weight)'.fmt(graph_fields.join(', '), graph_weight));

    var data = [];
    var node_id, node, node_dim, node_data, edge_id, edge, edge_width;

    var max_edge_weight = 0;
    var max_node_weight = 0;

    for (node_id in jsonData.nodes) {
        if (jsonData.nodes.hasOwnProperty(node_id)) {

            node = jsonData.nodes[node_id];

            if (node.weight > max_node_weight) {
                max_node_weight = node.weight;
            }

            for (edge_id in node.edges) {
                if (node.edges.hasOwnProperty(edge_id)) {

                    edge = node.edges[edge_id];

                    if (edge.weight > max_edge_weight) {
                        max_edge_weight = edge.weight;
                    }

                }
            }
        }
    }

    var MIN_NODE_DIM = 5;
    var MAX_NODE_DIM = 20;

    var MIN_LINE_WIDTH = 0.2;
    var MAX_LINE_WIDTH = 7;

    // Colors, catalog of types to colors
    // blue, red, olive, darkblue
    var colors = ["#006A80", "#801500", "#585800", "#000059"];
    var color_id = colors.length - 1;
    var catalog = {};

    function type_to_color(type) {
        if (! catalog.hasOwnProperty(type)) {
            color_id += 1;
            if (color_id >= colors.length){
                color_id = 0;
            }
            catalog[type] = colors[color_id];
        }
        return catalog[type];
    }

    for (node_id in jsonData.nodes) {
        if (jsonData.nodes.hasOwnProperty(node_id)) {

            node = jsonData.nodes[node_id];
            node_dim = Math.max(
                MIN_NODE_DIM,
                MAX_NODE_DIM * Math.sqrt(node.weight / max_node_weight));

            node_data = {
                'id'          : node_id,
                'name'        : node.name,
                'data'        : {
                    'weight' : node.weight,
                    'type'   : node.type,
                    "$color" : type_to_color(node.type),
                    "$type"  : "circle",
                    "$dim"   : node_dim
                },
                'adjacencies' : []
            };

            for (edge_id in node.edges) {
                if (node.edges.hasOwnProperty(edge_id)) {

                    edge = node.edges[edge_id];
                    edge_width = Math.max(
                        MIN_LINE_WIDTH,
                        MAX_LINE_WIDTH * edge.weight / max_edge_weight);

                    node_data.adjacencies.push({
                        'nodeFrom' : edge.from,
                        'nodeTo'   : edge.to,
                        'data'     : {
                            'weight'     : edge.weight,
                            "$color"     : "#585858",
                            '$lineWidth' : edge_width
                        }
                    });

                }
            }

            data.push(node_data);
        }
    }


    // Others
    // $jit.RGraph
    // $jit.Hypertree
    var fd = new $jit.ForceDirected({
        //id of the visualization container
        injectInto: 'infovis',
        //Enable zooming and panning
        //by scrolling and DnD
        Navigation: {
            enable: true,
            //Enable panning events only if we're dragging the empty
            //canvas (and not a node).
            panning: false, //'avoid nodes',
            zooming: 40 //zoom speed. higher is more sensible
        },
        // Change node and edge styles such as
        // color and width.
        // These properties are also set per node
        // with dollar prefixed data-properties in the
        // JSON structure.
        Node: {
            overridable: true
        },
        Edge: {
            overridable : true,
            color       : '#23A4FF',
            lineWidth   : 0.4
        },
        //Native canvas text styling
        Label: {
            type    : 'HTML', //Native or HTML
            size    : 10,
            style   : 'bold'
        },
        //Add Tips
        Tips: {
            enable: true,
            onShow: function(tip, node) {
                //count connections
                var count = 0;
                var list = [];

                node.eachAdjacency(function(adj) {
                    count += 1;
                    list.push([
                        adj.data.weight,
                        '[{0}] {1} (w. {2})'.fmt(adj.data.weight,
                                                 adj.nodeTo.name,
                                                 adj.nodeTo.data.weight)
                    ]);
                });

                // Sort by edge weight
                list.sort(function (a, b) {
                    return b[0] - a[0];
                });

                var i, c;
                var list_names = [];
                for (i=0, c=list.length; i<c; i++) {
                    list_names.push(list[i][1]);
                }

                // Build the right column relations list.
                // This is done by traversing the clicked node connections.
                var html = "";
                if (list_names.length !== 0){
                    html = "<ul><li>" + list_names.join("</li><li>") + "</li></ul>";
                }

                //display node info in tooltip
                tip.innerHTML = "" +
                    "<div class=\"tip-title\">{0}</div>".fmt(node.name) +
                    "<div class=\"tip-text\"><b>Weight {0}</b></div>".fmt(node.data.weight) +
                    "<div class=\"tip-text\"><b>Type {0}</b></div>".fmt(node.data.type) +
                    "<div class=\"tip-text\"><b>{0} link(s):</b> [link w.] node (node w.){1}</div>".fmt(count, html);
            }
        },
        // Add node events
        Events: {
            enable  : true,
            type    : 'Native',
            //Change cursor style when hovering a node
            onMouseEnter: function() {
                fd.canvas.getElement().style.cursor = 'move';
            },
            onMouseLeave: function() {
                fd.canvas.getElement().style.cursor = '';
            },
            //Update node positions when dragged
            onDragMove: function(node, eventInfo, e) {
                var pos = eventInfo.getPos();
                node.pos.setc(pos.x, pos.y);
                fd.plot();
            },
            //Implement the same handler for touchscreens
            onTouchMove: function(node, eventInfo, e) {
                $jit.util.event.stop(e); //stop default touchmove event
                this.onDragMove(node, eventInfo, e);
            },
            //Add also a click handler to nodes
            onClick: function(node) {
                if(!node) { return; }
            }
        },
        //Number of iterations for the FD algorithm
        iterations: 200,
        //Edge length
        levelDistance: 130,
        // Add text to the labels. This method is only triggered
        // on label creation and only for DOM labels (not native canvas ones).
        onCreateLabel: function(domElement, node){
            domElement.innerHTML = node.name;
            var style = domElement.style;
            style.fontSize = "0.80em";
            style.color = "#ddd";
        },
        // Change node styles when DOM labels are placed
        // or moved.
        onPlaceLabel: function(domElement, node){
            var style = domElement.style;
            var left = parseInt(style.left, 10);
            var top = parseInt(style.top, 10);
            var w = domElement.offsetWidth;
            style.left = (left - w / 2) + 'px';
            style.top = (top - 5) + 'px';
            style.display = '';
        }
    });

    // load JSON data.
    fd.loadJSON(data);

    var Log = {
        elem: false,
        write: function(text){
            if (!this.elem) {
                this.elem = document.getElementById('log');
            }
            this.elem.innerHTML = text;
            this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
        }
    };

    // compute positions incrementally and animate.
    fd.computeIncremental({
        iter    : 20,
        property: 'end',
        onStep  : function(perc){
            Log.write(perc + '% loaded...');
        },
        onComplete: function(){
            Log.write('done');
            fd.animate({
                modes       : ['linear'],
                transition  : $jit.Trans.Elastic.easeOut,
                duration    : 2500
            });
        }
    });

    // For other graphs
    //fd.refresh();
}


$(document).ready(function() {

    $("#infovis").css({
        "height": $(window).height() * 0.85
    });

    $("#infovis").css({
        "width": $(window).width() * 0.80
    });

    // JSON_FILE is defined in the template
    $.getJSON(JSON_FILE, function(data){
        initialize(data);
    });

});

