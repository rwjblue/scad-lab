/*
  Compact linked-dipole insulator. Units: mm; print broad face down.
  Default: two each of 40m, 30m and 20m, with recessed labels.
  Copyright 2026 rwjblue. Licensed CC BY-NC-SA 4.0:
  https://creativecommons.org/licenses/by-nc-sa/4.0/

  Initial wire: DX Engineering DXE-SANTW-500, 26 AWG stranded CCS,
  nominal insulated OD 0.041 in / 1.04 mm. The 1.8 mm holes include
  threading clearance. Connectors remain on relaxed external wire tails.

  Self-contained; compatible with OpenSCAD 2021.01 and newer.
  Body and labels exports share coordinates for a flush two-color print.
  Complete/recessed is a single-material print with empty letter pockets.
*/

/* [Output] */
layout = "starter"; // [starter:40m + 30m + 20m pairs, full:80m through 6m pairs, pair:Two with a custom label, single:One with a custom label]
pair_label = "40m";
part = "complete"; // [complete, body, labels]

/* [Fit] */
// Finished bore diameter, including print allowance; one wire per hole.
hole_d = 1.8; // [1.2:0.1:5]
// Width of the zip-tie band, not its larger head.
tie_width = 2.5; // [1.5:0.1:5]
thickness = 2.6; // [2:0.2:5]
// Minimum body size; larger holes, ties or labels grow it automatically.
min_length = 38; // [32:1:100]
min_width = 10; // [8:0.5:25]

/* [Label] */
label_style = "recessed"; // [recessed, raised, flush]
// Actual printed letter height; the body grows to retain readable labels.
label_size = 4.5; // [3:0.5:8]
label_depth = 0.4; // [0.2:0.1:1]
label_font = "Liberation Sans:style=Bold";

/* [Advanced] */
// Additional axial room around the tie band: 2.5 + 0.5 = 3 mm seat.
tie_clearance = 0.5; // [0.2:0.1:1]
// Inward relief on each long edge; zero omits the waist.
tie_relief = 0.75; // [0:0.05:1.5]
// Smooth transition length at each shoulder of the flat seat.
tie_shoulder = 0.75; // [0.5:0.05:2]
min_pitch = 6; // [5:0.5:15]
// 45-degree chamfer depth on both mouths of each wire hole.
hole_chamfer = 0.45; // [0.2:0.05:1]
edge_bevel = 0.25; // [0:0.05:0.5]
corner_radius = 3; // [1:0.5:5]
layout_gap = 4; // [3:1:15]

/* [Hidden] */
$fn = 64;
_eps = 0.01;
_label_margin = 0.8;
_min_web = 2;
_starter_labels = ["40m", "30m", "20m"];
_full_labels = ["80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m"];

function _contains(value, choices) = len([for (choice = choices) if (choice == value) 1]) > 0;
function _sum(values, i=0) = i >= len(values) ? 0 : values[i] + _sum(values, i+1);
function _clamp(value, lo, hi) = min(hi, max(lo, value));
function _smoothstep(t) = t*t*(3-2*t);

// Approximate glyph proportions establish a bounded label rectangle without
// experimental textmetrics(). resize() fits the complete text into that box;
// all glyphs, including accents/overhangs, remain clear of the wire holes.
function _glyph_width(c) =
    _contains(c, ["m", "M"]) ? 1.22 :
    _contains(c, ["W", "@", "%"]) ? 1.35 :
    c == "w" ? 1.12 :
    _contains(c, ["i", "l", "I", "!", ".", ",", ":", ";", "'", " "]) ? 0.40 :
    _contains(c, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]) ? 0.82 :
    _contains(c, ["f", "t", "j", "r", "(", ")", "-", "/"]) ? 0.60 : 0.94;

function link_label_size(label="40m") = label_size;
function link_thickness() = thickness;
function link_tie_width() = tie_width;
function link_neck_width() = link_width()-2*tie_relief;
function link_label_width(label="40m") =
    len(label) == 0 ? 0 : label_size * _sum([for (i = [0:len(label)-1]) _glyph_width(label[i])]);
function link_mouth_d() = hole_d + 2*hole_chamfer;
function link_seat_width() = tie_width + tie_clearance;
function link_pitch() = max(min_pitch, link_mouth_d() + link_seat_width() + 0.3);
function link_end_setback() = max(4, link_mouth_d()/2 + 2.5 + max(0, edge_bevel-0.25));
function link_inner_span(label="40m") =
    max(18, link_label_width(label) + link_mouth_d() + 2*_label_margin);
function link_length(label="40m") =
    max(min_length, 2*(link_end_setback()+link_pitch()) + link_inner_span(label));
function link_width() = max(min_width,
    label_size + 2*(_label_margin+edge_bevel),
    link_mouth_d() + 2*(_min_web+edge_bevel),
    2*tie_relief + link_mouth_d() + 2*_min_web);
function link_hole_x(label="40m", side=1, inner=false) =
    side*(link_length(label)/2-link_end_setback()-(inner ? link_pitch() : 0));
function link_tie_x(label="40m", side=1) =
    side*(link_length(label)/2-link_end_setback()-link_pitch()/2);
function link_labels() = layout == "starter" ? _starter_labels :
    layout == "full" ? _full_labels : [pair_label];
function link_copies() = layout == "single" ? 1 : 2;
function link_layout_length() = max([for (label = link_labels()) link_length(label)]);
function link_layout_x(copy) = (copy-(link_copies()-1)/2)*(link_layout_length()+layout_gap);
function link_layout_y(row) = ((len(link_labels())-1)/2-row)*(link_width()+layout_gap);

// C1 shoulders meet both the full-width edge and the flat seat tangentially.
function _waist_relief(x, center) =
    let(d = abs(x-center)-link_seat_width()/2)
    d <= 0 ? tie_relief : d >= tie_shoulder ? 0 :
    tie_relief*(1-_smoothstep(d/tie_shoulder));
function _top_y(x, label) = link_width()/2 -
    max(_waist_relief(x, link_tie_x(label, 1)),
        _waist_relief(x, link_tie_x(label, -1)));

// Sample each shoulder independently so the specified flat-seat width is
// exact and the shoulder endpoints remain vertices at every parameter size.
function _top_points(label) =
    let(L=link_length(label), W=link_width(), r=corner_radius,
        centers=[link_tie_x(label,-1),link_tie_x(label,1)],
        seat=link_seat_width()/2, n=16)
    concat([[-L/2+r,W/2]],
        [for (c=centers, k=[0:2*n+1])
            let(x = k <= n ? c-seat-tie_shoulder + tie_shoulder*k/n :
                    c+seat + tie_shoulder*(k-n-1)/n)
            [x,_top_y(x,label)]],
        [[L/2-r,W/2]]);
function _outline_points(label) =
    let(L=link_length(label),W=link_width(),r=corner_radius,n=24,
        top=_top_points(label))
    concat(top,
        [for(i=[1:n]) let(a=90-90*i/n) [L/2-r+r*cos(a), W/2-r+r*sin(a)]],
        [for(i=[0:n]) let(a=-90*i/n) [L/2-r+r*cos(a),-W/2+r+r*sin(a)]],
        [for(i=[len(top)-2:-1:0]) [top[i][0],-top[i][1]]],
        [for(i=[1:n]) let(a=-90-90*i/n) [-L/2+r+r*cos(a),-W/2+r+r*sin(a)]],
        [for(i=[0:n-1]) let(a=180-90*i/n) [-L/2+r+r*cos(a),W/2-r+r*sin(a)]]);

module _validate_link(label, component) {
    assert(_contains(component,["complete","body","labels"]), "Unknown component");
    assert(_contains(label_style,["recessed","raised","flush"]), "Unknown label style");
    assert(is_string(label) && len(label) <= 100, "Use a label of at most 100 characters");
    assert(hole_d >= 1.2 && hole_d <= 5, "Use 1.2-5 mm holes");
    assert(tie_width >= 1.5 && tie_width <= 5, "Use 1.5-5 mm tie bands");
    assert(tie_clearance >= 0.2 && tie_clearance <= 1, "Use 0.2-1 mm tie clearance");
    assert(tie_relief >= 0 && tie_relief <= 1.5, "Use 0-1.5 mm tie relief");
    assert(tie_shoulder >= 0.5 && tie_shoulder <= 2, "Use 0.5-2 mm shoulder transitions");
    assert(thickness >= 2 && thickness <= 5, "Use 2-5 mm plate thickness");
    assert(label_size >= 3 && label_size <= 8, "Use 3-8 mm lettering");
    assert(label_depth >= 0.2 && label_depth <= 1, "Use 0.2-1 mm label depth");
    assert(thickness-label_depth >= 1.6, "Leave at least 1.6 mm below the label");
    assert(hole_chamfer >= 0.2 && hole_chamfer <= 1 && 2*hole_chamfer < thickness,
        "Hole chamfers must leave a straight bore");
    assert(edge_bevel >= 0 && edge_bevel <= 0.5 && 2*edge_bevel < thickness,
        "Edge bevel must leave a full-thickness middle band");
    assert(corner_radius >= 1 && corner_radius <= link_width()/2,
        "Corner radius must fit within the plate width");
    assert(link_end_setback()+link_pitch()/2-link_seat_width()/2-tie_shoulder >= corner_radius,
        "Shorten the tie shoulder or reduce corner radius to keep the seat clear of the end curve");
    assert(link_pitch()-link_mouth_d() >= link_seat_width()+0.3-_eps,
        "Tie seat must fit between the hole mouths");
    assert(link_width()-2*tie_relief >= link_mouth_d()+2*_min_web,
        "Keep sufficient width through the tie waist");
    assert(link_length(label)-2*(link_end_setback()+link_pitch())-link_mouth_d()
        >= link_label_width(label)+2*_label_margin-_eps,
        "Label needs more room between inner holes");
    assert(min_length >= 32 && min_length <= 100 && min_width >= 8 && min_width <= 25,
        "Use 32-100 mm minimum length and 8-25 mm minimum width");
    assert(min_pitch >= 5 && min_pitch <= 15, "Use 5-15 mm minimum hole pitch");
    children();
}

module _outline(label) {
    polygon(_outline_points(label));
}

module _plate(label) {
    if (edge_bevel == 0) linear_extrude(height=thickness) _outline(label);
    else minkowski() {
        // A double cone sweeps a continuous 45-degree bevel around the
        // inset outline, retaining the flat tie seats and concave waists.
        translate([0,0,edge_bevel])
            linear_extrude(height=thickness-2*edge_bevel)
                offset(delta=-edge_bevel) _outline(label);
        union() {
            cylinder(r1=edge_bevel,r2=0,h=edge_bevel,$fn=32);
            mirror([0,0,1]) cylinder(r1=edge_bevel,r2=0,h=edge_bevel,$fn=32);
        }
    }
}

module _wire_hole() {
    translate([0,0,-_eps]) cylinder(d=hole_d,h=thickness+2*_eps);
    translate([0,0,-_eps])
        cylinder(d1=hole_d+2*(hole_chamfer+_eps),d2=hole_d,h=hole_chamfer+_eps);
    translate([0,0,thickness-hole_chamfer])
        cylinder(d1=hole_d,d2=hole_d+2*(hole_chamfer+_eps),h=hole_chamfer+_eps);
}

module _label_2d(label) {
    if (len(label) > 0)
        resize([link_label_width(label),label_size],auto=false)
            text(label,size=label_size,font=label_font,halign="center",valign="center");
}

module _label_solid(label, cut=false) {
    z=label_style == "raised" ? thickness : thickness-label_depth;
    // Extend a cutting tool above the face only. Keeping the exact floor
    // lets aligned flush lettering meet the body without an internal gap.
    translate([0,0,z])
        linear_extrude(height=label_depth+(cut ? _eps : 0)) _label_2d(label);
}

// Public single-link module; unchanged coordinates for body/labels exports.
module dipole_link(label="40m", component="complete") {
    _validate_link(label,component) {
        if (component != "labels") color([1,0.30,0.035]) difference() {
            _plate(label);
            for(side=[-1,1],inner=[false,true])
                translate([link_hole_x(label,side,inner),0,0]) _wire_hole();
            if(label_style != "raised") _label_solid(label,cut=true);
        }
        if(component == "labels" || (component == "complete" && label_style != "recessed"))
            color([0.12,0.12,0.12]) _label_solid(label);
    }
}

// Public plate module: matched pairs side by side, one band on each row.
module dipole_link_layout(component="complete") {
    assert(_contains(layout,["starter","full","pair","single"]), "Unknown layout");
    assert(layout_gap >= 3, "Leave at least 3 mm between links");
    labels=link_labels();
    for(row=[0:len(labels)-1],copy=[0:link_copies()-1])
        translate([link_layout_x(copy),link_layout_y(row),0])
            dipole_link(labels[row],component);
}

dipole_link_layout(part);
