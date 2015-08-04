function render_graph(graph_data, graph_area_selector, onclick_function) {

    var w = window.innerWidth;
    var h = window.innerHeight;

    var focus_node = null, highlight_node = null;

    var text_center = false;

    var min_score = 0;
    var max_score = 1;

    var color = d3.scale.linear()
      .domain([min_score, (min_score+max_score)/2, max_score])
      .range(["lime", "yellow", "red"]);

    var highlight_color = "blue";
    var highlight_trans = 0.1;

    var size = d3.scale.pow().exponent(1)
      .domain([1,100])
      .range([8,24]);

    var force = d3.layout.force()
      .linkDistance(60)
      .charge(-300)
      .size([w,h]);

    var selected_node = null;

    var default_node_color = "green"
    var default_node_border_color = "black"
    var selected_node_color = "red"
    var selected_node_border_color = "black"
    var highlighted_node_color = "blue"
    var highlighted_node_border_color = "black"

    var default_link_color = "#333";
    var selected_link_color = "red";
    var nominal_base_node_size = 8;
    var nominal_text_size = 10;
    var max_text_size = 24;
    var nominal_stroke = 1;
    var max_stroke = 4.5;
    var max_base_node_size = 36;
    var min_zoom = 0.1;
    var max_zoom = 7;
    var current_id = 0;
    var svg = d3.select(graph_area_selector).append("svg");
    var zoom = d3.behavior.zoom().scaleExtent([min_zoom,max_zoom]);
    var g = svg.append("g");


    svg.style("cursor","move");

    var graph = graph_data;
    var linkedByIndex = {};

    //clear graph
    svg.selectAll("g").selectAll("*").remove();

    graph.links.forEach(function (d) {
        linkedByIndex[d.source + "," + d.target] = true;
    });

    function isSelected(a, b) {
        return a.index == b.index;
    }
    function isConnected(a, b) {
        return linkedByIndex[a.index + "," + b.index] || linkedByIndex[b.index + "," + a.index] || a.index == b.index;
    }

    function hasConnections(a) {
        for (var property in linkedByIndex) {
            s = property.split(",");
            if ((s[0] == a.index || s[1] == a.index) && linkedByIndex[property])                    return true;
        }
        return false;
    }

    force
        .nodes(graph.nodes)
        .links(graph.links)
        .start();


    // build arrows.
    var arrows = svg.selectAll("marker")
        .data(["end"])      // Different link/path types can be defined here
        .enter().append("svg:marker")    // This section adds in the arrows
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 22)
        .attr("refY", -0.0)
        .attr("color", default_link_color)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");


    var link = g.selectAll(".link")
        .data(graph.links)
        .enter().append("line")
        .attr("class", function (d) {
            return "link " + d.type;
        })
        .attr("class", "link")
        .style("stroke-width", nominal_stroke)
        .style("stroke", function (d) {
            if (isNumber(d.score) && d.score >= 0) return color(d.score);
            else return default_link_color;
        }).attr("marker-end", function (d) {
            if (d.arrow) {
                return "url(#end)"
            } else {
                return ""
            }
        });

    var node = g.selectAll(".node")
                .data(graph.nodes)
                .enter().append("g")
                .attr("class", "node")
                .call(force.drag);

    var circle = node.append("path")
        .attr("d", d3.svg.symbol()
                .size(function (d) {
                    return Math.PI * Math.pow(size(d.size) || nominal_base_node_size, 2);
                })
                .type(function (d) {
                    return d.type;
                }))
        .attr("r", function(d) { return size(d.size)||nominal_base_node_size; })
            .style("stroke-width", nominal_stroke)
            .style('stroke', default_node_border_color)
            .style('fill', default_node_color)

    // Add fa icons
    var icons  = g.selectAll(".text").data(graph.nodes)
        .enter().append("text")
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .style("font-family", 'FontAwesome')
        .style("font-size", '17px')
        .text(function(d) { return window.FONT_AWESOME[d.icon]; });

    // Labels text
    var text = g.selectAll(".text")
            .data(graph.nodes)
            .enter().append("text")
            .attr("dy", ".35em")
            .attr("color", "#333")
            .style("font-size", nominal_text_size + "px")
            .text(function (d) {
                    return d.text
            });

    if (text_center) {
        text.style("text-anchor", "middle");
    }
    else {
        text.attr("dx", function (d) {
            return (10 || size(d.size) || 10);
        })
    }


    // Highlight

    node.on("mouseover", function (d) {
        set_highlight(d);
    });
    node.on("mousedown", function (d) {
        d3.event.stopPropagation();
        focus_node = d;
        set_focus(d);
        if (highlight_node === null) set_highlight(d)

    });
    node.on("mouseout", function (d) {
        exit_highlight();
    });

    d3.select(window).on("mouseup", function () {
        if (focus_node !== null) {
            focus_node = null;
            if (highlight_trans < 1) {
                circle.style("opacity", 1);
                text.style("opacity", 1);
                link.style("opacity", 1);
            }
        }
        if (highlight_node === null) exit_highlight();
    });

    function exit_highlight() {
        highlight_node = null;
        if (focus_node === null) {
            svg.style("cursor", "move");
            if (highlight_color != "white") {
                circle.style('fill', function (o) {
                if (selected_node && isSelected(selected_node, o)){
                    return selected_node_color
                }
                return default_node_color
            });
                text.style("font-weight", "normal");
                link.style("stroke", function (o) {
                    return (isNumber(o.score) && o.score >= 0) ? color(o.score) : default_link_color
                });
            }
        }
    }

    function set_focus(d) {
        if (highlight_trans < 1) {
            circle.style("opacity", function (o) {
                return isConnected(d, o) ? 1 : highlight_trans;
            });

            text.style("opacity", function (o) {
                return isConnected(d, o) ? 1 : highlight_trans;
            });

            link.style("opacity", function (o) {
                return o.source.index == d.index || o.target.index == d.index ? 1 : highlight_trans;
            });
        }
    }


    function set_highlight(d) {
        svg.style("cursor", "pointer");
        if (focus_node !== null) d = focus_node;
        highlight_node = d;

        if (highlight_color != "white") {
            circle.style('fill', function (o) {
                if (selected_node && isSelected(selected_node, o)){
                    return selected_node_color
                }
                if (isConnected(d, o)){
                    return highlighted_node_color
                }
                return default_node_color
            });
            text.style("font-weight", function (o) {
                return isConnected(d, o) ? "bold" : "normal";
            });
            link.style("stroke", function (o) {
                return o.source.index == d.index || o.target.index == d.index ? default_link_color : ((isNumber(o.score) && o.score >= 0) ? color(o.score) : default_link_color);
            });
        }
    }

    function highlight_selected() {
        if (selected_node){
            circle.style('fill', function (o) {
                    return isSelected(selected_node, o) ? selected_node_color : default_node_color;
            });
        }
    }

    // Zoom
    zoom.on("zoom", function () {
        var stroke = nominal_stroke;
        if (nominal_stroke * zoom.scale() > max_stroke) stroke = max_stroke / zoom.scale();
        link.style("stroke-width", stroke);
        circle.style("stroke-width", stroke);

        var base_radius = nominal_base_node_size;
        if (nominal_base_node_size * zoom.scale() > max_base_node_size) base_radius = max_base_node_size / zoom.scale();
        circle.attr("d", d3.svg.symbol()
                .size(function (d) {
                    return Math.PI * Math.pow(size(d.size) * base_radius / nominal_base_node_size || base_radius, 2);
                })
                .type(function (d) {
                    return d.type;
                }));

        //circle.attr("r", function(d) { return (size(d.size)*base_radius/nominal_base_node_size||base_radius); })
        if (!text_center) text.attr("dx", function (d) {
//            return (size(d.size) * base_radius / nominal_base_node_size || base_radius);
            return (10 * base_radius / nominal_base_node_size || base_radius);
        });

        var text_size = nominal_text_size;
        if (nominal_text_size * zoom.scale() > max_text_size) text_size = max_text_size / zoom.scale();
        text.style("font-size", text_size + "px");

        g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    });

    svg.call(zoom);

    resize();
    //window.focus();
    d3.select(window).on("resize", resize);

    force.on("tick", function () {
        node.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
        text.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
        icons.attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

        link.attr("x1", function (d) {
            return d.source.x;
        })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

        node.attr("cx", function (d) {
            return d.x;
        })
                .attr("cy", function (d) {
                    return d.y;
                });
    });

    function resize() {
        var rect = d3.select(".graph-area").node().getBoundingClientRect();
        var width = rect.width;
        var height = window.innerHeight;

        //            var svg_rect = svg.node().getBBox()
        //height = svg_rect.height;//window.innerHeight;
        svg.attr("width", width).attr("height", height);

        force.size([force.size()[0] + (width - w) / zoom.scale(), force.size()[1] + (height - h) / zoom.scale()]).resume();
        w = width;
        h = height;
    }


    function isNumber(n) {
        return !isNaN(parseFloat(n)) && isFinite(n);
    }


    node.on("dblclick", function (d) {
            d3.event.stopPropagation();
            window.open(d.link, '_blank');
    });

    node.on("click", function (d) {
        selected_node = d;
        highlight_selected(d)
        onclick_function(d)

    });
}