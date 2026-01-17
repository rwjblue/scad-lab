// Luggage Tag (simplified) based on v1.01 by Cristhian Valencia
//
// Original author: https://makerworld.com/en/@vlycser
// Original link: https://makerworld.com/en/models/710726
//
// This variant keeps only: first name, last name, phone number, email,
// and a vCard QR code. See models/luggage_tag/README.md for usage.
//
// License: CC BY-NC-ND 4.0
// https://creativecommons.org/licenses/by-nc-nd/4.0/
// Copyright (c) 2024 Cristhian Valencia

$fn = 120;
include <../../lib/qr.scad>

/* [Settings] */

Tag_Thickness   = 2;
Text_Thickness  = 0.7;
QR_Thickness    = 0.5;
QR_SIZE         = 50;

TAG_COLOR       = "#2B303A";
TEXT_COLOR      = "#92DCE5";
QR_COLOR        = "#92DCE5";
FONT_NAME       = "Liberation Sans";
FONT_STYLE      = "Bold";

/* [Personal Info] */

// Values are provided via the wrapper file or defaults in the module below.

/* [Hidden] */

TAG_EXTRUDE     = Tag_Thickness;
QR_EXTRUDE      = QR_Thickness;
LINES_EXTRUDE   = Text_Thickness;
QR_Z_POS        = TAG_EXTRUDE;
LINES_Z_POS     = TAG_EXTRUDE;
FONT_SCALE      = 0.154;
FONT            = str(FONT_NAME , ":style=", FONT_STYLE);

// Bezier calculation functions
function BEZ03(u) = pow((1-u), 3);
function BEZ13(u) = 3*u*(pow((1-u),2));
function BEZ23(u) = 3*(pow(u,2))*(1-u);
function BEZ33(u) = pow(u,3);

function bezier_2D_point(p0, p1, p2, p3, u) = [
    BEZ03(u)*p0[0] + BEZ13(u)*p1[0] + BEZ23(u)*p2[0] + BEZ33(u)*p3[0], 
    BEZ03(u)*p0[1] + BEZ13(u)*p1[1] + BEZ23(u)*p2[1] + BEZ33(u)*p3[1]
];

function bezier_coordinates(points, steps) = [
    for (c = points)
        for (step = [0:steps])
            bezier_2D_point(c[0], c[1], c[2], c[3], step/steps)
];

// Define the path data for Small Tag
S_OUTER_PATH = [
    [[156.25, -31.53], [156.25, -31.53], [127.22, -2.49], [127.22, -2.49]], [[127.22, -2.49], [125.63, -0.9000000000000001], [123.46, 0.0], [121.21, 0.0]], [[121.21, 0.0], [121.21, 0.0], [37.5, 0.0], [37.5, 0.0]], [[37.5, 0.0], [35.27, 0.0], [33.12, -0.88], [31.53, -2.45]], [[31.53, -2.45], [20.39, -13.42], [13.44, -20.54], [2.49, -31.52]], [[2.49, -31.52], [0.9, -33.12], [0.0, -35.28], [0.0, -37.54]], [[0.0, -37.54], [0.0, -37.54], [0.0, -274.97], [0.0, -274.97]], [[0.0, -274.97], [0.0, -279.67], [3.81, -283.47], [8.5, -283.47]], [[8.5, -283.47], [8.5, -283.47], [150.23, -283.47], [150.23, -283.47]], [[150.23, -283.47], [154.92999999999998, -283.47], [158.73, -279.66], [158.73, -274.97]], [[158.73, -274.97], [158.73, -274.97], [158.73, -37.54], [158.73, -37.54]], [[158.73, -37.54], [158.73, -35.28], [157.82999999999998, -33.12], [156.23999999999998, -31.53]], [[156.23999999999998, -31.53], [156.23999999999998, -31.53], [156.25, -31.53], [156.25, -31.53]], [[156.25, -31.53], [156.25, -31.53], [156.25, -31.53], [156.25, -31.53]]
];

S_INNER_PATH = [
    [[112.44, -30.03], [112.44, -30.03], [46.3, -30.03], [46.3, -30.03]], [[46.3, -30.03], [42.65, -30.03], [39.69, -26.86], [39.69, -22.94]], [[39.69, -22.94], [39.69, -19.020000000000003], [42.65, -15.850000000000001], [46.3, -15.850000000000001]], [[46.3, -15.850000000000001], [46.3, -15.850000000000001], [112.44, -15.850000000000001], [112.44, -15.850000000000001]], [[112.44, -15.850000000000001], [116.09, -15.850000000000001], [119.05, -19.020000000000003], [119.05, -22.94]], [[119.05, -22.94], [119.05, -26.86], [116.09, -30.03], [112.44, -30.03]], [[112.44, -30.03], [112.44, -30.03], [112.44, -30.03], [112.44, -30.03]], [[112.44, -30.03], [112.44, -30.03], [112.44, -30.03], [112.44, -30.03]]
];

module bezier_polygon(points) {
    color(TAG_COLOR) linear_extrude(height=TAG_EXTRUDE) {
        scale([0.35279, 0.35279, 1]) {
            polygon(bezier_coordinates(points, 30));
        }
    }
}

module create_tag_shape(outer_path, inner_path) {
    difference() {
        bezier_polygon(outer_path);
        bezier_polygon(inner_path);
    }
}

module CreateBaseTag(first_name, last_name, phone_number, email_address) {
    create_tag_shape(S_OUTER_PATH, S_INNER_PATH);

    // Add QR
    translate([3, -98, QR_Z_POS]) { CreateQR(first_name, last_name, phone_number, email_address); }

    // Add text lines
    TextExtrude(3, -25, LINES_Z_POS, first_name, TEXT_COLOR, 33, FONT, 1);
    TextExtrude(3, -32, LINES_Z_POS, last_name, TEXT_COLOR, 33, FONT, 1);
    TextExtrude(3, -41, LINES_Z_POS, phone_number, TEXT_COLOR, 24, FONT, 1);
}

module CreateQR(first_name, last_name, phone_number, email_address){
    QrMessage = qr_vcard(
        lastname=last_name,
        firstname=first_name,
        email=email_address,
        phone=phone_number
    );

    color(QR_COLOR) qr(QrMessage, error_correction="L", width=QR_SIZE, height=QR_SIZE, thickness=QR_EXTRUDE, center=false, mask_pattern=0, encoding="UTF-8");
}

module TextExtrude(X, Y, Z, Text, Color, FontSize, FontFamily, TextSpacing){
    translate([X, Y, Z]){
        color(Color) linear_extrude(height = LINES_EXTRUDE)
        text(Text, font = FontFamily, size = FontSize * FONT_SCALE, halign = "left", spacing = TextSpacing);
    }
}

// Create Tag
module luggage_tag(first_name="First", last_name="Last", phone_number="+1234567890", email_address="name@example.com") {
    translate([-28, 50]) { CreateBaseTag(first_name, last_name, phone_number, email_address); }
}

if (is_undef(LUGGAGE_TAG_NO_AUTORUN) || !LUGGAGE_TAG_NO_AUTORUN) {
    luggage_tag();
}
