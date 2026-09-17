// Fair-Rite 2631801202 winding cup; N1RWJ / Robert Jackson, CC BY-NC-SA 4.0.
// Units mm. Open underside at Z=0; core occupies Z=0..core_height.
// The two complete routes, cutters and diagnostics share the same coordinates.
/* [View] */
view = "print"; // [print,guide,wound,cutaway,debug,data]
/* [Measured core and fit] */
core_od = 29.00;
core_id = 19.00;
core_height = 13.85;
core_fit_clearance = 0.15; // Per radial surface, and above core; NOT diameter allowance
/* [Wire prototype - measure before printing] */
wire_od = 0.650; // Finished OD, advertised/unverified; bare copper approximately .644
wire_surface_gap = 0.100; // Enamel-to-enamel; electrical experiment, not a 50-ohm claim
groove_fit_clearance = 0.020; // RADIAL cutter clearance; never added to center spacing
groove_depth = 0.100; // Shallow open saddle, not a snap fit
supporting_wall_thickness = 0.500; // Minimum material behind a groove
edge_rounding = 1.000; // Exterior top corner radius; independent of backing thickness
/* [Layout] */
input_angle = -90; // Degrees in installed XY; -90 points toward BNC
output_angle = 90; // Opposite input, toward antenna posts
lead_reserve_angle = 24; // Clearance each side of input/output directions
crossover_clearance = 0.400; // Minimum wire surface clearance to unrelated winding
/* [Printing checks] */
minimum_printable_ridge = 0.250; // Fine .2 mm nozzle target; use .45 for ordinary .4 nozzle
minimum_printable_wall = 0.450;
strict_print_checks = false; // Turn advisory ridge/wall checks into assertions
/* [Hidden] */
$fn = 128;
arc_steps = 12;
curve_steps = 32;
wire_center_spacing = wire_od + wire_surface_gap;
groove_radius = wire_od/2 + groove_fit_clearance;
surface_offset = groove_radius - groove_depth;
// Compensate rounding of a square cavity corner to preserve minimum backing.
base_thickness = supporting_wall_thickness + groove_depth + 0.01; // Tessellation allowance
wall_thickness = max(base_thickness,
    (base_thickness + (sqrt(2)-1)*edge_rounding)/sqrt(2));
cavity_ro = core_od/2 + core_fit_clearance;
cavity_ri = core_id/2 - core_fit_clearance;
cavity_top = core_height + core_fit_clearance;
guide_ro = cavity_ro + wall_thickness;
guide_ri = cavity_ri - wall_thickness;
guide_top = cavity_top + wall_thickness;
pair_half = wire_center_spacing/2;
path_ro = sqrt(pow(guide_ro+surface_offset,2)-pow(pair_half,2));
path_ri = sqrt(pow(guide_ri-surface_offset,2)-pow(pair_half,2));
path_top = guide_top + surface_offset;
bend_r = edge_rounding + surface_offset;
rear_bend = 2.20; // Large rear bends preserve the backing at the open rim
rim_z = 0.65;
rear_z = rim_z - rear_bend;
groove_mouth = 2*sqrt(pow(groove_radius,2)-pow(surface_offset,2));
ridge_at_flat_surface = wire_center_spacing - groove_mouth;
full_cutter_separation = wire_center_spacing - 2*groove_radius;

function wg_core_height() = core_height;
function wg_rear_z() = rear_z;
function wg_wire_od() = wire_od;
function wg_spacing() = wire_center_spacing;
function wg_top() = guide_top;
function wg_diameter() = 2*guide_ro;
function wg_package_d() = 2*(guide_ro+surface_offset+wire_od/2);
function wg_package_h() = path_top+wire_od/2-(rear_z-wire_od/2);
function wg_rot(p,a) = [p[0]*cos(a)-p[1]*sin(a),p[0]*sin(a)+p[1]*cos(a),p[2]];
function wg_local(p,a,q) = wg_rot([p[0],q,p[1]],a);
function wg_bezier(a,b,c,d,t) = pow(1-t,3)*a + 3*pow(1-t,2)*t*b +
    3*(1-t)*t*t*c + t*t*t*d;
function wg_arc(cx,cz,r,a,b,n=arc_steps) =
    [for(i=[0:n]) [cx+r*cos(a+(b-a)*i/n),cz+r*sin(a+(b-a)*i/n)]];
function wg_angle(turn) = turn<=6 ?
    input_angle+lead_reserve_angle+(turn-1)*(180-2*lead_reserve_angle)/5 :
    turn==7 ? output_angle :
    input_angle-lead_reserve_angle-(turn-8)*(180-2*lead_reserve_angle)/5;
function wg_q(turn,strand) = (strand==0 ? -pair_half : pair_half)*(turn>=8 ? -1 : 1);
function wg_upper_profile() = concat(
    wg_arc(path_ro-rear_bend,rim_z,rear_bend,-90,0),
    [[path_ro,path_top-bend_r]],
    wg_arc(path_ro-bend_r,path_top-bend_r,bend_r,0,90),
    wg_arc(path_ri+bend_r,path_top-bend_r,bend_r,90,180));
function wg_lower_profile() = wg_arc(path_ri+rear_bend,rim_z,rear_bend,180,270);
function wg_turn_path(turn,strand) =
    turn!=7 ? [for(p=concat(wg_upper_profile(),wg_lower_profile()))
        wg_local(p,wg_angle(turn),wg_q(turn,strand))] :
    let(q=wg_q(7,strand), a=[path_ri,q,path_top-bend_r],
        b=[-path_ri,q,rim_z],
        upper=[for(p=wg_upper_profile()) wg_local(p,output_angle,q)],
        cross=[for(i=[1:curve_steps]) wg_rot(wg_bezier(a,a+[0,0,-3],
            b+[0,0,3],b,i/curve_steps),output_angle)],
        lower=[for(p=wg_lower_profile()) wg_local(p,input_angle,-q)])
    concat(upper,cross,lower);
function wg_end(turn,strand) = let(p=wg_turn_path(turn,strand)) p[len(p)-1];
function wg_start(turn,strand) = wg_turn_path(turn,strand)[0];
function wg_parallel_bezier(a,c,d,b,q) =
    [for(i=[0:curve_steps]) let(t=i/curve_steps,
        v=3*pow(1-t,2)*(c-a)+6*(1-t)*t*(d-c)+3*t*t*(b-d),
        n=[-v[1],v[0],0]/norm([v[0],v[1],0]))
        wg_bezier(a,c,d,b,t)+q*n];
function wg_link(turn,strand) =
    let(a=(wg_end(turn,0)+wg_end(turn,1))/2,
        b=(wg_start(turn+1,0)+wg_start(turn+1,1))/2,
        aa=turn==7 ? input_angle : wg_angle(turn),ba=wg_angle(turn+1),
        ra=wg_rot([1,0,0],aa), rb=wg_rot([1,0,0],ba),
        c=a+ra*1.4,d=b-rb*1.4,q=(strand==0 ? -pair_half : pair_half)*(turn>=7 ? -1 : 1))
    // Offset normal to the ACTUAL Bezier tangent, including underneath.
    // Interpolating two independently displaced curves can make wires collide.
    wg_parallel_bezier(a,c,d,b,q);
function wg_route(strand) = [for(t=[1:13]) each concat(wg_turn_path(t,strand),
    t<13 ? wg_link(t,strand) : [])];

module wg_tube(points,r,facets=16) {
    for(i=[0:len(points)-2]) if(norm(points[i+1]-points[i])>0.00001) hull() {
        translate(points[i]) sphere(r=r,$fn=facets);
        translate(points[i+1]) sphere(r=r,$fn=facets);
    }
}

function wg_clean(points) = [for(i=[0:len(points)-1])
    if(i==0 || norm(points[i]-points[i-1])>0.00001) points[i]];
function wg_unit(v) = v/norm(v);
function wg_tangent(p,i) = i==0 ? wg_unit(p[1]-p[0]) :
    i==len(p)-1 ? wg_unit(p[i]-p[i-1]) :
    wg_unit(wg_unit(p[i]-p[i-1])+wg_unit(p[i+1]-p[i]));
// One closed sweep per channel avoids coincident sphere-hull Boolean slivers.
// A constant binormal is valid because every numbered passage is planar.
// Circle rings remain inside the conservative capsule envelope used by checks.
module wg_channel(points,binormal,r,facets=24) {
    p=wg_clean(points);
    vertices=[for(i=[0:len(p)-1]) let(n=cross(wg_tangent(p,i),binormal))
        for(j=[0:facets-1]) p[i]+r*(binormal*cos(360*j/facets)+n*sin(360*j/facets))];
    faces=concat([[for(j=[facets-1:-1:0]) j]],
        [for(i=[0:len(p)-2],j=[0:facets-1])
            [i*facets+j,i*facets+(j+1)%facets,(i+1)*facets+(j+1)%facets,(i+1)*facets+j]],
        [[for(j=[0:facets-1]) (len(p)-1)*facets+j]]);
    // OpenSCAD polyhedron faces use clockwise order viewed from outside.
    polyhedron(points=vertices,faces=[for(f=faces) [for(j=[len(f)-1:-1:0]) f[j]]],convexity=10);
}

module wg_checks() {
    assert(core_od>core_id && core_id>0 && core_height>0,"Invalid core dimensions");
    assert(core_fit_clearance>=0 && groove_fit_clearance>=0,"Clearance must be nonnegative");
    assert(wire_od>0 && wire_surface_gap>=0,"Invalid wire dimensions");
    assert(groove_depth>0 && groove_depth<=groove_radius,"Use an open, shallow groove");
    assert(supporting_wall_thickness>0 && edge_rounding>0,"Backing/rounding must be positive");
    assert(guide_ri>pair_half+surface_offset && path_ro-path_ri>2*bend_r,
        "Rounding or wire size leaves no top face / aperture");
    assert(abs(output_angle-input_angle-180)<0.001,"Input and output must remain opposite");
    assert(lead_reserve_angle>=16 && lead_reserve_angle<55,"Lead reserve out of range");
    assert(crossover_clearance>=0,"Negative crossover clearance");
    assert(full_cutter_separation>0,"Paired channel cutters intersect: reduce clearance, not spacing");
    assert(2*path_ri*sin((180-2*lead_reserve_angle)/10)-wire_center_spacing>
        2*groove_radius,"Adjacent ordinary channels intersect at aperture");
    assert(2*path_ri*sin(lead_reserve_angle/2)-wire_center_spacing-wire_od>
        crossover_clearance,"Crossover landing interferes with adjacent turns");
    echo("PROTOTYPE: shallow grooves require a fine nozzle; free crossover and rear returns need manual spacing");
    if(wg_package_d()>34 || wg_package_h()>18)
        echo("FIT WARNING: increase the assembly wound-package allowance",wg_package_d(),wg_package_h());
    if(ridge_at_flat_surface<minimum_printable_ridge)
        echo("PRINT WARNING: ridge too narrow",ridge_at_flat_surface,minimum_printable_ridge);
    if(supporting_wall_thickness<minimum_printable_wall)
        echo("PRINT WARNING: insufficient backing",supporting_wall_thickness,minimum_printable_wall);
    assert(!strict_print_checks || ridge_at_flat_surface>=minimum_printable_ridge,
        "Ridge below selected printing threshold");
    assert(!strict_print_checks || supporting_wall_thickness>=minimum_printable_wall,
        "Backing below selected printing threshold");
    children();
}
module wg_shell() {
    // Rounded OUTSIDE top; square inside cavity accepts an unchamfered core.
    rotate_extrude(convexity=8) polygon(concat(
        [[guide_ro,0],[guide_ro,guide_top-edge_rounding]],
        wg_arc(guide_ro-edge_rounding,guide_top-edge_rounding,edge_rounding,0,90),
        wg_arc(guide_ri+edge_rounding,guide_top-edge_rounding,edge_rounding,90,180),
        [[guide_ri,0],[cavity_ri,0],[cavity_ri,cavity_top],
         [cavity_ro,cavity_top],[cavity_ro,0]]));
}
module winding_guide() {
    wg_checks() difference() {
        wg_shell();
        for(t=[1:13],s=[0,1]) wg_channel(wg_turn_path(t,s),wg_rot([0,1,0],wg_angle(t)),groove_radius);
    }
}
module winding_core() {
    color([.25,.27,.3]) difference() {
        cylinder(d=core_od,h=core_height);
        translate([0,0,-.01]) cylinder(d=core_id,h=core_height+.02);
    }
}
module winding_wires() {
    for(s=[0,1]) color(s==0 ? [.85,.22,.09] : [.07,.4,.95])
        wg_tube(wg_route(s),wire_od/2,12);
}
module winding_labels() {
    for(t=[1:13]) {
        a=wg_angle(t);
        color(t==7 ? [.55,.1,.65] : [.1,.1,.1])
            translate([(guide_ro+3)*cos(a),(guide_ro+3)*sin(a),guide_top+1])
            linear_extrude(.15) text(t==7 ? "7 X" : str(t),size=2,halign="center",valign="center");
    }
    color([.55,.1,.65]) translate([0,0,path_top+1])
        linear_extrude(.15) text("7",size=2,halign="center");
    for(a=[input_angle,output_angle])
        color([.15,.15,.15]) translate([0,(guide_ro+7)*sin(a),guide_top+1])
        linear_extrude(.15) text(a==input_angle ? "IN / BNC" : "OUT / POSTS",size=2,halign="center");
}
module winding_assembly(debug=false,cutaway=false) {
    winding_core();
    color([.93,.8,.42]) difference() {
        winding_guide();
        if(cutaway) translate([0,-guide_ro-1,-1])
            cube([guide_ro+1,guide_ro+1,guide_top+2]);
    }
    winding_wires();
    if(debug) winding_labels();
}
module wg_data() {
    wg_checks() {
        echo("PARAMS",[core_od,core_id,core_height,core_fit_clearance,wire_od,
            wire_surface_gap,groove_fit_clearance,groove_depth,supporting_wall_thickness,
            edge_rounding,crossover_clearance]);
        echo("METRICS",[wire_center_spacing,groove_radius,wall_thickness,guide_ro,
            guide_ri,guide_top,ridge_at_flat_surface,full_cutter_separation,
            wg_package_d(),wg_package_h(),rear_z]);
        for(t=[1:13],s=[0,1]) echo("TURN",t,s,wg_turn_path(t,s));
        for(s=[0,1]) echo("ROUTE",s,wg_route(s));
    }
}

if(view=="print") translate([0,0,guide_top]) rotate([180,0,0]) winding_guide();
else if(view=="guide") color([.93,.8,.42]) winding_guide();
else if(view=="wound") winding_assembly();
else if(view=="cutaway") winding_assembly(cutaway=true);
else if(view=="debug") winding_assembly(true);
else if(view=="data") wg_data();
else assert(false,"Unknown view");
