import type { Constraint } from '../planegcs_dist/constraints';
import type { oid, Id } from '../planegcs_dist/id';
interface IArc {
    start_id: oid;
    end_id: oid;
    start_angle: number;
    end_angle: number;
}
export interface SketchPoint extends Id {
    type: 'point';
    x: number;
    y: number;
    fixed: boolean;
}
export interface SketchLine extends Id {
    type: 'line';
    p1_id: oid;
    p2_id: oid;
}
export interface SketchCircle extends Id {
    type: 'circle';
    c_id: oid;
    radius: number;
}
export interface SketchArc extends Id, IArc {
    type: 'arc';
    c_id: oid;
    radius: number;
}
export interface SketchEllipse extends Id {
    type: 'ellipse';
    c_id: oid;
    focus1_id: oid;
    radmin: number;
}
export interface SketchArcOfEllipse extends Id, IArc {
    type: 'arc_of_ellipse';
    c_id: oid;
    focus1_id: oid;
    radmin: number;
}
export interface SketchParabola extends Id {
    type: 'parabola';
    vertex_id: oid;
    focus1_id: oid;
}
export interface SketchArcOfParabola extends Id, IArc {
    type: 'arc_of_parabola';
    vertex_id: oid;
    focus1_id: oid;
}
export interface SketchHyperbola extends Id {
    type: 'hyperbola';
    c_id: oid;
    focus1_id: oid;
    radmin: number;
}
export interface SketchArcOfHyperbola extends Id, IArc {
    type: 'arc_of_hyperbola';
    c_id: oid;
    focus1_id: oid;
    radmin: number;
}
export type SketchGeometry = SketchPoint | SketchLine | SketchCircle | SketchArc | SketchEllipse | SketchArcOfEllipse | SketchParabola | SketchArcOfParabola | SketchHyperbola | SketchArcOfHyperbola;
export type SketchPrimitive = SketchGeometry | Constraint;
export interface SketchParam {
    type: 'param';
    name: string;
    value: number;
}
export declare function is_sketch_geometry(primitive: SketchPrimitive | SketchParam | undefined): primitive is SketchGeometry;
export declare function is_sketch_constraint(primitive: SketchPrimitive | SketchParam | undefined): primitive is Constraint;
export declare function get_referenced_sketch_params(p: SketchPrimitive): string[];
export declare function for_each_referenced_id(p: SketchPrimitive, f: (id: oid) => oid | undefined): void;
export declare function get_constrained_primitive_ids(p: SketchPrimitive): oid[];
export {};
