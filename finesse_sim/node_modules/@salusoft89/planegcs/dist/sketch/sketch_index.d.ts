import type { SketchPoint, SketchLine, SketchCircle, SketchArc, SketchPrimitive } from "./sketch_primitive";
import type { Constraint } from "../planegcs_dist/constraints";
import { oid } from "../planegcs_dist/id";
export declare abstract class SketchIndexBase {
    abstract get_primitives(): SketchPrimitive[];
    abstract get_primitive(id: oid): SketchPrimitive | undefined;
    abstract set_primitive(obj: SketchPrimitive): void;
    abstract delete_primitive(id: oid): boolean;
    abstract clear(): void;
    abstract has(id: oid): boolean;
    get_primitive_or_fail(id: oid): SketchPrimitive;
    get_sketch_point(id: oid): SketchPoint;
    get_sketch_line(id: oid): SketchLine;
    get_sketch_circle(id: oid): SketchCircle;
    get_sketch_arc(id: oid): SketchArc;
    get_constraints(): Constraint[];
    toString(): string;
}
export declare class SketchIndex extends SketchIndexBase {
    index: Map<oid, SketchPrimitive>;
    primitive_ids: oid[];
    has(id: oid): boolean;
    delete_primitive(id: oid): boolean;
    set_primitive(obj: SketchPrimitive): void;
    get_primitive(id: oid): SketchPrimitive | undefined;
    get_primitives(): (SketchPrimitive)[];
    get_id_by_index(index: number): oid;
    clear(): void;
    counter(): number;
}
