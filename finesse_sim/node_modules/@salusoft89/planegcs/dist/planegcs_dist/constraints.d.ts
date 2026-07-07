import { SketchGeometryProperty } from "../sketch/geom_params";
import { InternalAlignmentType, Constraint_Alignment } from "./enums";
import type { oid, Id } from "./id";
interface ObjectParam {
    o_id: oid;
    prop: SketchGeometryProperty;
}
export interface Equal extends Id {
    type: 'equal';
    param1: ObjectParam | number | string;
    param2: ObjectParam | number | string;
    driving?: boolean;
    internalalignment?: Constraint_Alignment;
    temporary?: boolean;
    scale?: number;
}
export interface Proportional extends Id {
    type: 'proportional';
    param1: ObjectParam | number | string;
    param2: ObjectParam | number | string;
    ratio: number;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Difference extends Id {
    type: 'difference';
    param1: ObjectParam | number | string;
    param2: ObjectParam | number | string;
    difference: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2PDistance extends Id {
    type: 'p2p_distance';
    p1_id: oid;
    p2_id: oid;
    distance: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2PAngle_INCR_ANGLE extends Id {
    type: 'p2p_angle_incr_angle';
    p1_id: oid;
    p2_id: oid;
    angle: ObjectParam | number | string;
    incrAngle: number;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2PAngle extends Id {
    type: 'p2p_angle';
    p1_id: oid;
    p2_id: oid;
    angle: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2LDistance extends Id {
    type: 'p2l_distance';
    p_id: oid;
    l_id: oid;
    distance: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnLine_PL extends Id {
    type: 'point_on_line_pl';
    p_id: oid;
    l_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnLine_PPP extends Id {
    type: 'point_on_line_ppp';
    p_id: oid;
    lp1_id: oid;
    lp2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnPerpBisector_PL extends Id {
    type: 'point_on_perp_bisector_pl';
    p_id: oid;
    l_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnPerpBisector_PPP extends Id {
    type: 'point_on_perp_bisector_ppp';
    p_id: oid;
    lp1_id: oid;
    lp2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Parallel extends Id {
    type: 'parallel';
    l1_id: oid;
    l2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Perpendicular_LL extends Id {
    type: 'perpendicular_ll';
    l1_id: oid;
    l2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Perpendicular_PPPP extends Id {
    type: 'perpendicular_pppp';
    l1p1_id: oid;
    l1p2_id: oid;
    l2p1_id: oid;
    l2p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface L2LAngle_LL extends Id {
    type: 'l2l_angle_ll';
    l1_id: oid;
    l2_id: oid;
    angle: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface L2LAngle_PPPP extends Id {
    type: 'l2l_angle_pppp';
    l1p1_id: oid;
    l1p2_id: oid;
    l2p1_id: oid;
    l2p2_id: oid;
    angle: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface AngleViaPoint extends Id {
    type: 'angle_via_point';
    crv1_id: oid;
    crv2_id: oid;
    p_id: oid;
    angle: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface AngleViaTwoPoints extends Id {
    type: 'angle_via_two_points';
    crv1_id: oid;
    crv2_id: oid;
    p1_id: oid;
    p2_id: oid;
    angle: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface AngleViaPointAndParam extends Id {
    type: 'angle_via_point_and_param';
    crv1_id: oid;
    crv2_id: oid;
    p_id: oid;
    cparam: ObjectParam | number | string;
    angle: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface AngleViaPointAndTwoParams extends Id {
    type: 'angle_via_point_and_two_params';
    crv1_id: oid;
    crv2_id: oid;
    p_id: oid;
    cparam1: ObjectParam | number | string;
    cparam2: ObjectParam | number | string;
    angle: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface MidpointOnLine_LL extends Id {
    type: 'midpoint_on_line_ll';
    l1_id: oid;
    l2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface MidpointOnLine_PPPP extends Id {
    type: 'midpoint_on_line_pppp';
    l1p1_id: oid;
    l1p2_id: oid;
    l2p1_id: oid;
    l2p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface TangentCircumf extends Id {
    type: 'tangent_circumf';
    p1_id: oid;
    p2_id: oid;
    rd1: ObjectParam | number | string;
    rd2: ObjectParam | number | string;
    internal?: boolean;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface TangentAtBSplineKnot extends Id {
    type: 'tangent_at_bspline_knot';
    b_id: oid;
    l_id: oid;
    knotindex: number;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2PCoincident extends Id {
    type: 'p2p_coincident';
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Horizontal_L extends Id {
    type: 'horizontal_l';
    l_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Horizontal_PP extends Id {
    type: 'horizontal_pp';
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Vertical_L extends Id {
    type: 'vertical_l';
    l_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Vertical_PP extends Id {
    type: 'vertical_pp';
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface CoordinateX extends Id {
    type: 'coordinate_x';
    p_id: oid;
    x: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface CoordinateY extends Id {
    type: 'coordinate_y';
    p_id: oid;
    y: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface ArcRules extends Id {
    type: 'arc_rules';
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnCircle extends Id {
    type: 'point_on_circle';
    p_id: oid;
    c_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnEllipse extends Id {
    type: 'point_on_ellipse';
    p_id: oid;
    e_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnHyperbolicArc extends Id {
    type: 'point_on_hyperbolic_arc';
    p_id: oid;
    e_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnParabolicArc extends Id {
    type: 'point_on_parabolic_arc';
    p_id: oid;
    e_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnBSpline extends Id {
    type: 'point_on_bspline';
    p_id: oid;
    b_id: oid;
    pointparam: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface ArcOfEllipseRules extends Id {
    type: 'arc_of_ellipse_rules';
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface CurveValue extends Id {
    type: 'curve_value';
    p_id: oid;
    a_id: oid;
    u: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface ArcOfHyperbolaRules extends Id {
    type: 'arc_of_hyperbola_rules';
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface ArcOfParabolaRules extends Id {
    type: 'arc_of_parabola_rules';
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PointOnArc extends Id {
    type: 'point_on_arc';
    p_id: oid;
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PerpendicularLine2Arc extends Id {
    type: 'perpendicular_line2arc';
    p1_id: oid;
    p2_id: oid;
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PerpendicularArc2Line extends Id {
    type: 'perpendicular_arc2line';
    a_id: oid;
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PerpendicularCircle2Arc extends Id {
    type: 'perpendicular_circle2arc';
    center_id: oid;
    radius: ObjectParam | number | string;
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PerpendicularArc2Circle extends Id {
    type: 'perpendicular_arc2circle';
    a_id: oid;
    center_id: oid;
    radius: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface PerpendicularArc2Arc extends Id {
    type: 'perpendicular_arc2arc';
    a1_id: oid;
    reverse1: boolean;
    a2_id: oid;
    reverse2: boolean;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Tangent_LC extends Id {
    type: 'tangent_lc';
    l_id: oid;
    c_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Tangent_LE extends Id {
    type: 'tangent_le';
    l_id: oid;
    e_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Tangent_LA extends Id {
    type: 'tangent_la';
    l_id: oid;
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Tangent_CC extends Id {
    type: 'tangent_cc';
    c1_id: oid;
    c2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Tangent_AA extends Id {
    type: 'tangent_aa';
    a1_id: oid;
    a2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface Tangent_CA extends Id {
    type: 'tangent_ca';
    c_id: oid;
    a_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface CircleRadius extends Id {
    type: 'circle_radius';
    c_id: oid;
    radius: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface ArcRadius extends Id {
    type: 'arc_radius';
    a_id: oid;
    radius: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface CircleDiameter extends Id {
    type: 'circle_diameter';
    c_id: oid;
    diameter: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface ArcDiameter extends Id {
    type: 'arc_diameter';
    a_id: oid;
    diameter: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface EqualLength extends Id {
    type: 'equal_length';
    l1_id: oid;
    l2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface EqualRadius_CC extends Id {
    type: 'equal_radius_cc';
    c1_id: oid;
    c2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface EqualRadii_EE extends Id {
    type: 'equal_radii_ee';
    e1_id: oid;
    e2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface EqualRadii_AHAH extends Id {
    type: 'equal_radii_ahah';
    a1_id: oid;
    a2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface EqualRadius_CA extends Id {
    type: 'equal_radius_ca';
    c1_id: oid;
    a2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface EqualRadius_AA extends Id {
    type: 'equal_radius_aa';
    a1_id: oid;
    a2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface EqualFocus extends Id {
    type: 'equal_focus';
    a1_id: oid;
    a2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2PSymmetric_PPL extends Id {
    type: 'p2p_symmetric_ppl';
    p1_id: oid;
    p2_id: oid;
    l_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2PSymmetric_PPP extends Id {
    type: 'p2p_symmetric_ppp';
    p1_id: oid;
    p2_id: oid;
    p_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface SnellsLaw extends Id {
    type: 'snells_law';
    ray1_id: oid;
    ray2_id: oid;
    boundary_id: oid;
    p_id: oid;
    n1: ObjectParam | number | string;
    n2: ObjectParam | number | string;
    flipn1: boolean;
    flipn2: boolean;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface C2CDistance extends Id {
    type: 'c2cdistance';
    c1_id: oid;
    c2_id: oid;
    dist: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface C2LDistance extends Id {
    type: 'c2ldistance';
    c_id: oid;
    l_id: oid;
    dist: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface P2CDistance extends Id {
    type: 'p2cdistance';
    p_id: oid;
    c_id: oid;
    distance: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface ArcLength extends Id {
    type: 'arc_length';
    a_id: oid;
    dist: ObjectParam | number | string;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentPoint2Ellipse extends Id {
    type: 'internal_alignment_point2ellipse';
    e_id: oid;
    p1_id: oid;
    alignmentType: InternalAlignmentType;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentEllipseMajorDiameter extends Id {
    type: 'internal_alignment_ellipse_major_diameter';
    e_id: oid;
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentEllipseMinorDiameter extends Id {
    type: 'internal_alignment_ellipse_minor_diameter';
    e_id: oid;
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentEllipseFocus1 extends Id {
    type: 'internal_alignment_ellipse_focus1';
    e_id: oid;
    p1_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentEllipseFocus2 extends Id {
    type: 'internal_alignment_ellipse_focus2';
    e_id: oid;
    p1_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentPoint2Hyperbola extends Id {
    type: 'internal_alignment_point2hyperbola';
    e_id: oid;
    p1_id: oid;
    alignmentType: InternalAlignmentType;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentHyperbolaMajorDiameter extends Id {
    type: 'internal_alignment_hyperbola_major_diameter';
    e_id: oid;
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentHyperbolaMinorDiameter extends Id {
    type: 'internal_alignment_hyperbola_minor_diameter';
    e_id: oid;
    p1_id: oid;
    p2_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentHyperbolaFocus extends Id {
    type: 'internal_alignment_hyperbola_focus';
    e_id: oid;
    p1_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentParabolaFocus extends Id {
    type: 'internal_alignment_parabola_focus';
    e_id: oid;
    p1_id: oid;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentBSplineControlPoint extends Id {
    type: 'internal_alignment_bspline_control_point';
    b_id: oid;
    c_id: oid;
    poleindex: number;
    tag?: number;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export interface InternalAlignmentKnotPoint extends Id {
    type: 'internal_alignment_knot_point';
    b_id: oid;
    p_id: oid;
    knotindex: number;
    driving?: boolean;
    temporary?: boolean;
    scale?: number;
}
export type Constraint = Equal | Proportional | Difference | P2PDistance | P2PAngle_INCR_ANGLE | P2PAngle | P2LDistance | PointOnLine_PL | PointOnLine_PPP | PointOnPerpBisector_PL | PointOnPerpBisector_PPP | Parallel | Perpendicular_LL | Perpendicular_PPPP | L2LAngle_LL | L2LAngle_PPPP | AngleViaPoint | AngleViaTwoPoints | AngleViaPointAndParam | AngleViaPointAndTwoParams | MidpointOnLine_LL | MidpointOnLine_PPPP | TangentCircumf | TangentAtBSplineKnot | P2PCoincident | Horizontal_L | Horizontal_PP | Vertical_L | Vertical_PP | CoordinateX | CoordinateY | ArcRules | PointOnCircle | PointOnEllipse | PointOnHyperbolicArc | PointOnParabolicArc | PointOnBSpline | ArcOfEllipseRules | CurveValue | ArcOfHyperbolaRules | ArcOfParabolaRules | PointOnArc | PerpendicularLine2Arc | PerpendicularArc2Line | PerpendicularCircle2Arc | PerpendicularArc2Circle | PerpendicularArc2Arc | Tangent_LC | Tangent_LE | Tangent_LA | Tangent_CC | Tangent_AA | Tangent_CA | CircleRadius | ArcRadius | CircleDiameter | ArcDiameter | EqualLength | EqualRadius_CC | EqualRadii_EE | EqualRadii_AHAH | EqualRadius_CA | EqualRadius_AA | EqualFocus | P2PSymmetric_PPL | P2PSymmetric_PPP | SnellsLaw | C2CDistance | C2LDistance | P2CDistance | ArcLength | InternalAlignmentPoint2Ellipse | InternalAlignmentEllipseMajorDiameter | InternalAlignmentEllipseMinorDiameter | InternalAlignmentEllipseFocus1 | InternalAlignmentEllipseFocus2 | InternalAlignmentPoint2Hyperbola | InternalAlignmentHyperbolaMajorDiameter | InternalAlignmentHyperbolaMinorDiameter | InternalAlignmentHyperbolaFocus | InternalAlignmentParabolaFocus | InternalAlignmentBSplineControlPoint | InternalAlignmentKnotPoint;
export type ConstraintParamType = Equal[keyof Equal] | Proportional[keyof Proportional] | Difference[keyof Difference] | P2PDistance[keyof P2PDistance] | P2PAngle_INCR_ANGLE[keyof P2PAngle_INCR_ANGLE] | P2PAngle[keyof P2PAngle] | P2LDistance[keyof P2LDistance] | PointOnLine_PL[keyof PointOnLine_PL] | PointOnLine_PPP[keyof PointOnLine_PPP] | PointOnPerpBisector_PL[keyof PointOnPerpBisector_PL] | PointOnPerpBisector_PPP[keyof PointOnPerpBisector_PPP] | Parallel[keyof Parallel] | Perpendicular_LL[keyof Perpendicular_LL] | Perpendicular_PPPP[keyof Perpendicular_PPPP] | L2LAngle_LL[keyof L2LAngle_LL] | L2LAngle_PPPP[keyof L2LAngle_PPPP] | AngleViaPoint[keyof AngleViaPoint] | AngleViaTwoPoints[keyof AngleViaTwoPoints] | AngleViaPointAndParam[keyof AngleViaPointAndParam] | AngleViaPointAndTwoParams[keyof AngleViaPointAndTwoParams] | MidpointOnLine_LL[keyof MidpointOnLine_LL] | MidpointOnLine_PPPP[keyof MidpointOnLine_PPPP] | TangentCircumf[keyof TangentCircumf] | TangentAtBSplineKnot[keyof TangentAtBSplineKnot] | P2PCoincident[keyof P2PCoincident] | Horizontal_L[keyof Horizontal_L] | Horizontal_PP[keyof Horizontal_PP] | Vertical_L[keyof Vertical_L] | Vertical_PP[keyof Vertical_PP] | CoordinateX[keyof CoordinateX] | CoordinateY[keyof CoordinateY] | ArcRules[keyof ArcRules] | PointOnCircle[keyof PointOnCircle] | PointOnEllipse[keyof PointOnEllipse] | PointOnHyperbolicArc[keyof PointOnHyperbolicArc] | PointOnParabolicArc[keyof PointOnParabolicArc] | PointOnBSpline[keyof PointOnBSpline] | ArcOfEllipseRules[keyof ArcOfEllipseRules] | CurveValue[keyof CurveValue] | ArcOfHyperbolaRules[keyof ArcOfHyperbolaRules] | ArcOfParabolaRules[keyof ArcOfParabolaRules] | PointOnArc[keyof PointOnArc] | PerpendicularLine2Arc[keyof PerpendicularLine2Arc] | PerpendicularArc2Line[keyof PerpendicularArc2Line] | PerpendicularCircle2Arc[keyof PerpendicularCircle2Arc] | PerpendicularArc2Circle[keyof PerpendicularArc2Circle] | PerpendicularArc2Arc[keyof PerpendicularArc2Arc] | Tangent_LC[keyof Tangent_LC] | Tangent_LE[keyof Tangent_LE] | Tangent_LA[keyof Tangent_LA] | Tangent_CC[keyof Tangent_CC] | Tangent_AA[keyof Tangent_AA] | Tangent_CA[keyof Tangent_CA] | CircleRadius[keyof CircleRadius] | ArcRadius[keyof ArcRadius] | CircleDiameter[keyof CircleDiameter] | ArcDiameter[keyof ArcDiameter] | EqualLength[keyof EqualLength] | EqualRadius_CC[keyof EqualRadius_CC] | EqualRadii_EE[keyof EqualRadii_EE] | EqualRadii_AHAH[keyof EqualRadii_AHAH] | EqualRadius_CA[keyof EqualRadius_CA] | EqualRadius_AA[keyof EqualRadius_AA] | EqualFocus[keyof EqualFocus] | P2PSymmetric_PPL[keyof P2PSymmetric_PPL] | P2PSymmetric_PPP[keyof P2PSymmetric_PPP] | SnellsLaw[keyof SnellsLaw] | C2CDistance[keyof C2CDistance] | C2LDistance[keyof C2LDistance] | P2CDistance[keyof P2CDistance] | ArcLength[keyof ArcLength] | InternalAlignmentPoint2Ellipse[keyof InternalAlignmentPoint2Ellipse] | InternalAlignmentEllipseMajorDiameter[keyof InternalAlignmentEllipseMajorDiameter] | InternalAlignmentEllipseMinorDiameter[keyof InternalAlignmentEllipseMinorDiameter] | InternalAlignmentEllipseFocus1[keyof InternalAlignmentEllipseFocus1] | InternalAlignmentEllipseFocus2[keyof InternalAlignmentEllipseFocus2] | InternalAlignmentPoint2Hyperbola[keyof InternalAlignmentPoint2Hyperbola] | InternalAlignmentHyperbolaMajorDiameter[keyof InternalAlignmentHyperbolaMajorDiameter] | InternalAlignmentHyperbolaMinorDiameter[keyof InternalAlignmentHyperbolaMinorDiameter] | InternalAlignmentHyperbolaFocus[keyof InternalAlignmentHyperbolaFocus] | InternalAlignmentParabolaFocus[keyof InternalAlignmentParabolaFocus] | InternalAlignmentBSplineControlPoint[keyof InternalAlignmentBSplineControlPoint] | InternalAlignmentKnotPoint[keyof InternalAlignmentKnotPoint];
export {};
