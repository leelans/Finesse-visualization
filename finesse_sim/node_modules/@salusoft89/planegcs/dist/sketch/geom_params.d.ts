import { SketchGeometry } from "./sketch_primitive.js";
export type SketchGeometryProperty = 'x' | 'y' | 'radius' | 'start_angle' | 'end_angle' | 'radmin';
export declare const property_offsets: {
    readonly point: {
        readonly x: 0;
        readonly y: 1;
    };
    readonly circle: {
        readonly radius: 0;
    };
    readonly arc: {
        readonly start_angle: 0;
        readonly end_angle: 1;
        readonly radius: 2;
    };
    readonly ellipse: {
        readonly radmin: 0;
    };
    readonly arc_of_ellipse: {
        readonly start_angle: 0;
        readonly end_angle: 1;
        readonly radmin: 2;
    };
    readonly parabola: {};
    readonly arc_of_parabola: {
        readonly start_angle: 0;
        readonly end_angle: 1;
    };
    readonly hyperbola: {
        readonly radmin: 0;
    };
    readonly arc_of_hyperbola: {
        readonly start_angle: 0;
        readonly end_angle: 1;
        readonly radmin: 2;
    };
    readonly line: {};
};
export default function get_property_offset(primitive_type: SketchGeometry['type'], property_key: SketchGeometryProperty): number;
